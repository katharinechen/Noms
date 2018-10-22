"""
Management of fulltext indexes over the recipe database
"""
from __future__ import print_function

import os, os.path
from pipes import quote

from codado.py import fromdir

import click

from whoosh import index
from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID
from whoosh.qparser import QueryParser

from tqdm import tqdm

from mongoengine import connect

from noms import DBHost
from noms.recipe import Recipe


INDEX_PATH = fromdir()('recipe.search')


class RecipeSchema(SchemaClass):
    name = TEXT(field_boost=2.0, stored=True)
    author = TEXT(stored=True)
    user = TEXT
    urlKey = ID(stored=True)
    ingredients = TEXT
    instructions = TEXT
    recipeYield = TEXT
    tags = KEYWORD(field_boost=3.0, commas=True, scorable=True, lowercase=True, stored=True)
    combined = TEXT


def getOrCreateIndex(pth=INDEX_PATH):
    """
    Initialize a text index if missing; otherwise access it
    """
    if not os.path.exists(pth):
        os.mkdir(pth)

        ix = index.create_in(pth, RecipeSchema)
    else:
        ix = index.open_dir(pth)

    return ix


@click.command()
@click.argument("phrase", nargs=-1)
@click.option("--build", is_flag=True, help='kick off a build of a new index')
@click.option("--alias", default='noms', help='Alias for a database connection (see noms.DBAlias)')
def srch(phrase, build, alias):
    """
    Execute an index search or build the index
    """
    ix = getOrCreateIndex()
    if build:
        with ix.writer() as writer:
            connect(**DBHost[alias])
            total = Recipe.objects.count()
            for rec in tqdm(Recipe.objects(), total=total):
                ings = u'\n'.join(rec.ingredients)
                ins = u'\n'.join(rec.instructions)
                tags = u','.join(rec.tags)
                comb = u'\n'.join([
                    rec.name,
                    rec.author,
                    ings,
                    ins,
                    tags,
                ])
                writer.add_document(
                    name=rec.name,
                    author=rec.author,
                    user=rec.user.email,
                    urlKey=rec.urlKey,
                    ingredients=ings,
                    instructions=ins,
                    recipeYield=rec.recipeYield,
                    tags=tags,
                    combined=comb,
                )
            return
    else:
        qp = QueryParser('combined', schema=RecipeSchema())
        rawQuery = u' '.join([quote(w) for w in phrase])
        query = qp.parse(rawQuery)
        with ix.searcher() as searcher:
            result = searcher.search(query)
            for r in result:
                print(r)


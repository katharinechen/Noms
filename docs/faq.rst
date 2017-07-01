Frequently Asked Questions
==========================

**How do I see a list of all of the urls in ``Noms``?**
Run ``urltool`` in the terminal. You can filter for all API urls by doing ``urltool /api``. 

**Where does our 3rd party libraries live?**

We have a s3 bucket called ``cloudfront.nomsbook.com``. In the s3 bucket, we are going to put all the cloudfront 3rd party javascript files we need (e.g. font-awesome).

To add a file to the nomsbook s3 bucket: 
- Log in to your s3 management console (https://goonmill-org.signin.aws.amazon.com/console)
- View your buckets. You should have a cloudfront.nomsbook.com s3 bucket.
- Add the file you want.
- When you upload, expand "Manage public permissions" and check "Read" for Everyone.

We are making own cdn on Amazon's cloudfront for the following reasons: 
- CDN host by other people might not be reliable
- Hosting on our own Amazon cdn is more reliable, and within our control
- We also don't have to worry about the security of other websites beside our own
# Teardown checklist (do this every time)

Neptune is not free-tier eligible, and Bedrock and Neptune Analytics bill while
they exist. After every AWS lab, delete in this order and confirm each is gone:

1. **Neptune notebook** (SageMaker notebook instance): stop, then delete.
2. **Neptune Database** cluster: delete every instance, then the cluster
   (skip the final snapshot for lab data). Check *Neptune > Databases* is empty.
3. **Neptune Analytics** graph: delete it. Check *Neptune > Analytics > Graphs*.
4. **Bedrock Knowledge Base** and its data source (if you built Section 13.6's
   managed GraphRAG). The vector store it created goes with it, but check.
5. **S3**: empty and delete the lab bucket.
6. **IAM**: delete the lab roles and policies you created.
7. **VPC endpoints / NAT gateways** created for the lab: a NAT gateway bills
   hourly even when idle.

Then open *Billing > Bills* the next day and confirm nothing from the lab is
still accruing. Setting an AWS Budget with an email alert at a few dollars is
a sensible guard before you start.

# AWS VPC peering approval and route or DNS configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-vpc-peering-connections.md`
- Source Title: `Connect to TiDB Cloud Dedicated via VPC Peering`
- Source Heading Path: `Connect to TiDB Cloud Dedicated via VPC Peering > Set up VPC peering on AWS > Step 2. Approve and configure the VPC peering`
- Source Line Ranges: `121-247`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `vpc-peering`, `aws`, `aws-cli`, `aws-console`, `route-tables`, `dns`, `networking`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0270_6fcd9ca39b`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-vpc-peering-connections.md#step-2-approve-and-configure-the-vpc-peering`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6c469785584ab0edce3ea1f4a7d356141895f740a4a1f75e6289e62cbbe5f8c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-vpc-peering-connections#step-2-approve-and-configure-the-vpc-peering
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-vpc-peering-connections.md

## Retrieval Guidance

- Use When: Use this chunk when you need the AWS steps to approve a TiDB Cloud Dedicated VPC peering request and configure route tables or DNS settings for verification.
- Retrieval Keywords: AWS VPC peering, approve and configure the VPC peering, aws ec2 accept-vpc-peering-connection, aws ec2 create-route, aws ec2 describe-route-tables, aws ec2 modify-vpc-attribute, enable-dns-hostnames, enable-dns-support, Peering Connections, Pending Acceptance, Route Tables, Edit routes, TiDB Cloud Project VPC CIDR, TiDB Cloud AWS Account ID, TiDB Cloud VPC ID, An error occurred (MissingParameter) when calling the CreateRoute operation: The request must contain the parameter routeTableId
- Follow-up Guidance: After finishing the configuration, the source says the VPC peering has been created and you can connect to the TiDB cluster to verify the result.
- Classification Note: This chunk is classified as configuration because it contains the AWS CLI commands and AWS Management Console steps to accept the peering request, add route table entries, and enable DNS settings.

## Official Source Content

### Step 2. Approve and configure the VPC peering

You can approve and configure the VPC peering connection using AWS CLI or AWS dashboard.

<div label="Use AWS CLI">

1. Install AWS Command Line Interface (AWS CLI).

    ```bash
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    ```

2. Configure AWS CLI according to your account information. To get the information required by AWS CLI, see [AWS CLI configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

    ```bash
    aws configure
    ```

3. Replace the following variable values with your account information.

    ```bash
    # Sets up the related variables.
    pcx_tidb_to_app_id="<TiDB peering id>"
    app_region="<APP Region>"
    app_vpc_id="<Your VPC ID>"
    tidbcloud_project_cidr="<TiDB Cloud Project VPC CIDR>"
    ```

    For example:

    ```
    # Sets up the related variables
    pcx_tidb_to_app_id="pcx-069f41efddcff66c8"
    app_region="us-west-2"
    app_vpc_id="vpc-0039fb90bb5cf8698"
    tidbcloud_project_cidr="10.250.0.0/16"
    ```

4. Run the following commands.

    ```bash
    # Accepts the VPC peering connection request.
    aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id "$pcx_tidb_to_app_id"
    ```

    ```bash
    # Creates route table rules.
    aws ec2 describe-route-tables --region "$app_region" --filters Name=vpc-id,Values="$app_vpc_id" --query 'RouteTables[*].RouteTableId' --output text | tr "\t" "\n" | while read row
    do
        app_route_table_id="$row"
        aws ec2 create-route --region "$app_region" --route-table-id "$app_route_table_id" --destination-cidr-block "$tidbcloud_project_cidr" --vpc-peering-connection-id "$pcx_tidb_to_app_id"
    done
    ```

    > **Note:**
    >
    > Sometimes, even if the route table rules are successfully created, you might still get the `An error occurred (MissingParameter) when calling the CreateRoute operation: The request must contain the parameter routeTableId` error. In this case, you can check the created rules and ignore the error.

    ```bash
    # Modifies the VPC attribute to enable DNS-hostname and DNS-support.
    aws ec2 modify-vpc-attribute --vpc-id "$app_vpc_id" --enable-dns-hostnames
    aws ec2 modify-vpc-attribute --vpc-id "$app_vpc_id" --enable-dns-support
    ```

After finishing the configuration, the VPC peering has been created. You can [connect to the TiDB cluster](#connect-to-the-tidb-cluster) to verify the result.

</div>
<div label="Use the AWS dashboard">

You can also use the AWS dashboard to configure the VPC peering connection.

1. Confirm to accept the peer connection request in your [AWS Management Console](https://console.aws.amazon.com/).

    1. Sign in to the [AWS Management Console](https://console.aws.amazon.com/) and click **Services** on the top menu bar. Enter `VPC` in the search box and go to the VPC service page.

        ![AWS dashboard](/media/tidb-cloud/vpc-peering/aws-vpc-guide-1.jpg)

    2. From the left navigation bar, open the **Peering Connections** page. On the **Create Peering Connection** tab, a peering connection is in the **Pending Acceptance** status.

    3. Confirm that the requester owner and the requester VPC match **TiDB Cloud AWS Account ID** and **TiDB Cloud VPC ID** on the **VPC Peering Details** page of the [TiDB Cloud console](https://tidbcloud.com). Right-click the peering connection and select **Accept Request** to accept the request in the **Accept VPC peering connection request** dialog.

        ![AWS VPC peering requests](/media/tidb-cloud/vpc-peering/aws-vpc-guide-3.png)

2. Add a route to the TiDB Cloud VPC for each of your VPC subnet route tables.

    1. From the left navigation bar, open the **Route Tables** page.

    2. Search all the route tables that belong to your application VPC.

        ![Search all route tables related to VPC](/media/tidb-cloud/vpc-peering/aws-vpc-guide-4.png)

    3. Right-click each route table and select **Edit routes**. On the edit page, add a route with a destination to the TiDB Cloud CIDR (by checking the **VPC Peering** configuration page in the TiDB Cloud console) and fill in your peering connection ID in the **Target** column.

        ![Edit all route tables](/media/tidb-cloud/vpc-peering/aws-vpc-guide-5.png)

3. Make sure you have enabled private DNS hosted zone support for your VPC.

    1. From the left navigation bar, open the **Your VPCs** page.

    2. Select your application VPC.

    3. Right click on the selected VPC. The setting drop-down list displays.

    4. From the setting drop-down list, click **Edit DNS hostnames**. Enable DNS hostnames and click **Save**.

    5. From the setting drop-down list, click **Edit DNS resolution**. Enable DNS resolution and click **Save**.

Now you have successfully set up the VPC peering connection. Next, [connect to the TiDB cluster via VPC peering](#connect-to-the-tidb-cluster).

</div>

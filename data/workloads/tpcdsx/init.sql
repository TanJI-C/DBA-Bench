-- TPC-DSX Initialization

-- 
-- Legal Notice 
-- 
-- This document and associated source code (the "Work") is a part of a 
-- benchmark specification maintained by the TPC. 
-- 
-- The TPC reserves all right, title, and interest to the Work as provided 
-- under U.S. and international laws, including without limitation all patent 
-- and trademark rights therein. 
-- 
-- No Warranty 
-- 
-- 1.1 TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE INFORMATION 
--     CONTAINED HEREIN IS PROVIDED "AS IS" AND WITH ALL FAULTS, AND THE 
--     AUTHORS AND DEVELOPERS OF THE WORK HEREBY DISCLAIM ALL OTHER 
--     WARRANTIES AND CONDITIONS, EITHER EXPRESS, IMPLIED OR STATUTORY, 
--     INCLUDING, BUT NOT LIMITED TO, ANY (IF ANY) IMPLIED WARRANTIES, 
--     DUTIES OR CONDITIONS OF MERCHANTABILITY, OF FITNESS FOR A PARTICULAR 
--     PURPOSE, OF ACCURACY OR COMPLETENESS OF RESPONSES, OF RESULTS, OF 
--     WORKMANLIKE EFFORT, OF LACK OF VIRUSES, AND OF LACK OF NEGLIGENCE. 
--     ALSO, THERE IS NO WARRANTY OR CONDITION OF TITLE, QUIET ENJOYMENT, 
--     QUIET POSSESSION, CORRESPONDENCE TO DESCRIPTION OR NON-INFRINGEMENT 
--     WITH REGARD TO THE WORK. 
-- 1.2 IN NO EVENT WILL ANY AUTHOR OR DEVELOPER OF THE WORK BE LIABLE TO 
--     ANY OTHER PARTY FOR ANY DAMAGES, INCLUDING BUT NOT LIMITED TO THE 
--     COST OF PROCURING SUBSTITUTE GOODS OR SERVICES, LOST PROFITS, LOSS 
--     OF USE, LOSS OF DATA, OR ANY INCIDENTAL, CONSEQUENTIAL, DIRECT, 
--     INDIRECT, OR SPECIAL DAMAGES WHETHER UNDER CONTRACT, TORT, WARRANTY,
--     OR OTHERWISE, ARISING IN ANY WAY OUT OF THIS OR ANY OTHER AGREEMENT 
--     RELATING TO THE WORK, WHETHER OR NOT SUCH AUTHOR OR DEVELOPER HAD 
--     ADVANCE NOTICE OF THE POSSIBILITY OF SUCH DAMAGES. 
-- 
-- Contributors:
-- Gradient Systems
--
create table data_build_info
(
    bi_version                varchar(16)                   ,
    bi_create_date            date                          ,
    bi_create_time            time                          ,
    bi_cmdline_args           varchar(200)                  
);

create table account_address
(
    aa_address_sk             integer               not null,
    aa_address_id             char(16)              not null,
    aa_street_number          char(10)                      ,
    aa_street_name            varchar(60)                   ,
    aa_street_type            char(15)                      ,
    aa_suite_number           char(10)                      ,
    aa_city                   varchar(60)                   ,
    aa_county                 varchar(30)                   ,
    aa_state                  char(2)                       ,
    aa_zip                    char(10)                      ,
    aa_country                varchar(20)                   ,
    aa_gmt_offset             decimal(5,2)                  ,
    aa_location_type          char(20)                      ,
    primary key (aa_address_sk)
);

create table account_profile
(
    ap_profile_sk                integer               not null,
    ap_gender                 char(1)                       ,
    ap_marital_status         char(1)                       ,
    ap_education_status       char(20)                      ,
    ap_purchase_estimate      integer                       ,
    ap_credit_rating          char(10)                      ,
    ap_dep_count              integer                       ,
    ap_dep_employed_count     integer                       ,
    ap_dep_college_count      integer                       ,
    primary key (ap_profile_sk)
);

create table calendar_day
(
    cal_day_sk                 integer               not null,
    cal_day_id                 char(16)              not null,
    cal_date                    date                          ,
    cal_month_seq               integer                       ,
    cal_week_seq                integer                       ,
    cal_quarter_seq             integer                       ,
    cal_year                    integer                       ,
    cal_dow                     integer                       ,
    cal_moy                     integer                       ,
    cal_dom                     integer                       ,
    cal_qoy                     integer                       ,
    cal_fy_year                 integer                       ,
    cal_fy_quarter_seq          integer                       ,
    cal_fy_week_seq             integer                       ,
    cal_day_name                char(9)                       ,
    cal_quarter_name            char(6)                       ,
    cal_holiday                 char(1)                       ,
    cal_weekend                 char(1)                       ,
    cal_following_holiday       char(1)                       ,
    cal_first_dom               integer                       ,
    cal_last_dom                integer                       ,
    cal_same_day_ly             integer                       ,
    cal_same_day_lq             integer                       ,
    cal_current_day             char(1)                       ,
    cal_current_week            char(1)                       ,
    cal_current_month           char(1)                       ,
    cal_current_quarter         char(1)                       ,
    cal_current_year            char(1)                       ,
    primary key (cal_day_sk)
);

create table fulfillment_site
(
    fs_site_sk            integer               not null,
    fs_site_id            char(16)              not null,
    fs_site_name          varchar(20)                   ,
    fs_site_sq_ft         integer                       ,
    fs_street_number           char(10)                      ,
    fs_street_name             varchar(60)                   ,
    fs_street_type             char(15)                      ,
    fs_suite_number            char(10)                      ,
    fs_city                    varchar(60)                   ,
    fs_county                  varchar(30)                   ,
    fs_state                   char(2)                       ,
    fs_zip                     char(10)                      ,
    fs_country                 varchar(20)                   ,
    fs_gmt_offset              decimal(5,2)                  ,
    primary key (fs_site_sk)
);

create table delivery_method
(
    dm_method_sk           integer               not null,
    dm_method_id           char(16)              not null,
    dm_type                   char(30)                      ,
    dm_code                   char(10)                      ,
    dm_carrier                char(20)                      ,
    dm_contract               char(20)                      ,
    primary key (dm_method_sk)
);

create table clock_time
(
    ct_time_sk                 integer               not null,
    ct_time_id                 char(16)              not null,
    ct_time_value                    integer                       ,
    ct_hour                    integer                       ,
    ct_minute                  integer                       ,
    ct_second                  integer                       ,
    ct_am_pm                   char(2)                       ,
    ct_shift                   char(20)                      ,
    ct_sub_shift               char(20)                      ,
    ct_meal_time               char(20)                      ,
    primary key (ct_time_sk)
);

create table return_reason
(
    rr_reason_sk               integer               not null,
    rr_reason_id               char(16)              not null,
    rr_reason_desc             char(100)                     ,
    primary key (rr_reason_sk)
);

create table budget_band
(
    bb_band_sk         integer               not null,
    bb_lower_bound            integer                       ,
    bb_upper_bound            integer                       ,
    primary key (bb_band_sk)
);

create table product
(
    pr_product_sk                 integer               not null,
    pr_product_id                 char(16)              not null,
    pr_rec_start_date          date                          ,
    pr_rec_end_date            date                          ,
    pr_product_desc               varchar(200)                  ,
    pr_current_price           decimal(7,2)                  ,
    pr_wholesale_cost          decimal(7,2)                  ,
    pr_brand_id                integer                       ,
    pr_brand                   char(50)                      ,
    pr_class_id                integer                       ,
    pr_class                   char(50)                      ,
    pr_category_id             integer                       ,
    pr_category                char(50)                      ,
    pr_manufact_id             integer                       ,
    pr_manufact                char(50)                      ,
    pr_size                    char(20)                      ,
    pr_formulation             char(20)                      ,
    pr_color                   char(20)                      ,
    pr_units                   char(10)                      ,
    pr_container               char(10)                      ,
    pr_manager_id              integer                       ,
    pr_product_name            char(50)                      ,
    primary key (pr_product_sk)
);

create table branch
(
    br_branch_sk                integer               not null,
    br_branch_id                char(16)              not null,
    br_rec_start_date          date                          ,
    br_rec_end_date            date                          ,
    br_closed_date_sk          integer                       ,
    br_branch_name              varchar(50)                   ,
    br_number_employees        integer                       ,
    br_floor_space             integer                       ,
    br_hours                   char(20)                      ,
    br_manager                 varchar(40)                   ,
    br_market_id               integer                       ,
    br_geography_class         varchar(100)                  ,
    br_market_desc             varchar(100)                  ,
    br_market_manager          varchar(40)                   ,
    br_division_id             integer                       ,
    br_division_name           varchar(50)                   ,
    br_company_id              integer                       ,
    br_company_name            varchar(50)                   ,
    br_street_number           varchar(10)                   ,
    br_street_name             varchar(60)                   ,
    br_street_type             char(15)                      ,
    br_suite_number            char(10)                      ,
    br_city                    varchar(60)                   ,
    br_county                  varchar(30)                   ,
    br_state                   char(2)                       ,
    br_zip                     char(10)                      ,
    br_country                 varchar(20)                   ,
    br_gmt_offset              decimal(5,2)                  ,
    br_tax_percentage          decimal(5,2)                  ,
    primary key (br_branch_sk)
);

create table service_center
(
    sc_center_sk         integer               not null,
    sc_center_id         char(16)              not null,
    sc_rec_start_date         date                          ,
    sc_rec_end_date           date                          ,
    sc_closed_date_sk         integer                       ,
    sc_open_date_sk           integer                       ,
    sc_name                   varchar(50)                   ,
    sc_class                  varchar(50)                   ,
    sc_employees              integer                       ,
    sc_sq_ft                  integer                       ,
    sc_hours                  char(20)                      ,
    sc_manager                varchar(40)                   ,
    sc_market_id                 integer                       ,
    sc_market_class              char(50)                      ,
    sc_market_desc               varchar(100)                  ,
    sc_market_manager         varchar(40)                   ,
    sc_division_id               integer                       ,
    sc_division_name          varchar(50)                   ,
    sc_company_id                integer                       ,
    sc_company_name           char(50)                      ,
    sc_street_number          char(10)                      ,
    sc_street_name            varchar(60)                   ,
    sc_street_type            char(15)                      ,
    sc_suite_number           char(10)                      ,
    sc_city                   varchar(60)                   ,
    sc_county                 varchar(30)                   ,
    sc_state                  char(2)                       ,
    sc_zip                    char(10)                      ,
    sc_country                varchar(20)                   ,
    sc_gmt_offset             decimal(5,2)                  ,
    sc_tax_percentage         decimal(5,2)                  ,
    primary key (sc_center_sk)
);

create table shopper_account
(
    sa_account_sk             integer               not null,
    sa_account_id             char(16)              not null,
    sa_current_profile_sk        integer                       ,
    sa_current_household_sk        integer                       ,
    sa_current_addr_sk         integer                       ,
    sa_first_shipto_date_sk    integer                       ,
    sa_first_purchase_date_sk     integer                       ,
    sa_salutation              char(10)                      ,
    sa_first_name              char(20)                      ,
    sa_last_name               char(30)                      ,
    sa_preferred_flag     char(1)                       ,
    sa_birth_day               integer                       ,
    sa_birth_month             integer                       ,
    sa_birth_year              integer                       ,
    sa_birth_country           varchar(20)                   ,
    sa_login                   char(13)                      ,
    sa_email_address           char(50)                      ,
    sa_last_review_date_sk     integer                       ,
    primary key (sa_account_sk)
);

create table digital_site
(
    ds_site_sk               integer               not null,
    ds_site_id               char(16)              not null,
    ds_rec_start_date        date                          ,
    ds_rec_end_date          date                          ,
    ds_name                  varchar(50)                   ,
    ds_open_date_sk          integer                       ,
    ds_close_date_sk         integer                       ,
    ds_class                 varchar(50)                   ,
    ds_manager               varchar(40)                   ,
    ds_market_id                integer                       ,
    ds_market_class             varchar(50)                   ,
    ds_market_desc              varchar(100)                  ,
    ds_market_manager        varchar(40)                   ,
    ds_company_id            integer                       ,
    ds_company_name          char(50)                      ,
    ds_street_number         char(10)                      ,
    ds_street_name           varchar(60)                   ,
    ds_street_type           char(15)                      ,
    ds_suite_number          char(10)                      ,
    ds_city                  varchar(60)                   ,
    ds_county                varchar(30)                   ,
    ds_state                 char(2)                       ,
    ds_zip                   char(10)                      ,
    ds_country               varchar(20)                   ,
    ds_gmt_offset            decimal(5,2)                  ,
    ds_tax_percentage        decimal(5,2)                  ,
    primary key (ds_site_sk)
);

create table branch_returns
(
    bret_returned_date_sk       integer                       ,
    bret_return_time_sk         integer                       ,
    bret_product_sk                integer               not null,
    bret_account_sk            integer                       ,
    bret_profile_sk               integer                       ,
    bret_household_sk               integer                       ,
    bret_addr_sk                integer                       ,
    bret_branch_sk               integer                       ,
    bret_reason_sk              integer                       ,
    bret_receipt_number          integer               not null,
    bret_return_quantity        integer                       ,
    bret_return_amt             decimal(7,2)                  ,
    bret_return_tax             decimal(7,2)                  ,
    bret_return_amt_inc_tax     decimal(7,2)                  ,
    bret_fee                    decimal(7,2)                  ,
    bret_return_ship_cost       decimal(7,2)                  ,
    bret_refunded_cash          decimal(7,2)                  ,
    bret_reversed_charge        decimal(7,2)                  ,
    bret_branch_credit           decimal(7,2)                  ,
    bret_net_loss               decimal(7,2)                  ,
    primary key (bret_product_sk, bret_receipt_number)
);

create table household_profile
(
    hp_profile_sk                integer               not null,
    hp_budget_band_sk         integer                       ,
    hp_buy_potential          char(15)                      ,
    hp_dep_count              integer                       ,
    hp_vehicle_count          integer                       ,
    primary key (hp_profile_sk)
);

create table digital_page
(
    dp_page_sk            integer               not null,
    dp_page_id            char(16)              not null,
    dp_rec_start_date         date                          ,
    dp_rec_end_date           date                          ,
    dp_creation_date_sk       integer                       ,
    dp_access_date_sk         integer                       ,
    dp_autogen_flag           char(1)                       ,
    dp_account_sk            integer                       ,
    dp_url                    varchar(100)                  ,
    dp_type                   char(50)                      ,
    dp_char_count             integer                       ,
    dp_link_count             integer                       ,
    dp_image_count            integer                       ,
    dp_max_ad_count           integer                       ,
    primary key (dp_page_sk)
);

create table campaign
(
    camp_campaign_sk                integer               not null,
    camp_campaign_id                char(16)              not null,
    camp_start_date_sk           integer                       ,
    camp_end_date_sk             integer                       ,
    camp_product_sk                 integer                       ,
    camp_cost                    decimal(15,2)                 ,
    camp_response_target         integer                       ,
    camp_campaign_name              char(50)                      ,
    camp_channel_dmail           char(1)                       ,
    camp_channel_email           char(1)                       ,
    camp_channel_catalog         char(1)                       ,
    camp_channel_tv              char(1)                       ,
    camp_channel_radio           char(1)                       ,
    camp_channel_press           char(1)                       ,
    camp_channel_event           char(1)                       ,
    camp_channel_demo            char(1)                       ,
    camp_channel_details         varchar(100)                  ,
    camp_purpose                 char(15)                      ,
    camp_discount_active         char(1)                       ,
    primary key (camp_campaign_sk)
);

create table catalog_section
(
    csec_section_sk        integer               not null,
    csec_section_id        char(16)              not null,
    csec_start_date_sk          integer                       ,
    csec_end_date_sk            integer                       ,
    csec_department             varchar(50)                   ,
    csec_catalog_number         integer                       ,
    csec_page_number    integer                       ,
    csec_description            varchar(100)                  ,
    csec_type                   varchar(100)                  ,
    primary key (csec_section_sk)
);

create table stock_snapshot
(
    stk_date_sk               integer               not null,
    stk_product_sk               integer               not null,
    stk_site_sk          integer               not null,
    stk_quantity_on_hand      integer                       ,
    primary key (stk_date_sk, stk_product_sk, stk_site_sk)
);

create table assisted_returns
(
    aret_returned_date_sk       integer                       ,
    aret_returned_time_sk       integer                       ,
    aret_product_sk                integer               not null,
    aret_refunded_account_sk   integer                       ,
    aret_refunded_profile_sk      integer                       ,
    aret_refunded_household_sk      integer                       ,
    aret_refunded_addr_sk       integer                       ,
    aret_returning_account_sk  integer                       ,
    aret_returning_profile_sk     integer                       ,
    aret_returning_household_sk     integer                       ,
    aret_returning_addr_sk      integer                       ,
    aret_service_center_sk         integer                       ,
    aret_catalog_section_sk        integer                       ,
    aret_delivery_method_sk           integer                       ,
    aret_site_sk           integer                       ,
    aret_reason_sk              integer                       ,
    aret_order_number           integer               not null,
    aret_return_quantity        integer                       ,
    aret_return_amount          decimal(7,2)                  ,
    aret_return_tax             decimal(7,2)                  ,
    aret_return_amt_inc_tax     decimal(7,2)                  ,
    aret_fee                    decimal(7,2)                  ,
    aret_return_ship_cost       decimal(7,2)                  ,
    aret_refunded_cash          decimal(7,2)                  ,
    aret_reversed_charge        decimal(7,2)                  ,
    aret_branch_credit           decimal(7,2)                  ,
    aret_net_loss               decimal(7,2)                  ,
    primary key (aret_product_sk, aret_order_number)
);

create table digital_returns
(
    dret_returned_date_sk       integer                       ,
    dret_returned_time_sk       integer                       ,
    dret_product_sk                integer               not null,
    dret_refunded_account_sk   integer                       ,
    dret_refunded_profile_sk      integer                       ,
    dret_refunded_household_sk      integer                       ,
    dret_refunded_addr_sk       integer                       ,
    dret_returning_account_sk  integer                       ,
    dret_returning_profile_sk     integer                       ,
    dret_returning_household_sk     integer                       ,
    dret_returning_addr_sk      integer                       ,
    dret_page_sk            integer                       ,
    dret_reason_sk              integer                       ,
    dret_order_number           integer               not null,
    dret_return_quantity        integer                       ,
    dret_return_amt             decimal(7,2)                  ,
    dret_return_tax             decimal(7,2)                  ,
    dret_return_amt_inc_tax     decimal(7,2)                  ,
    dret_fee                    decimal(7,2)                  ,
    dret_return_ship_cost       decimal(7,2)                  ,
    dret_refunded_cash          decimal(7,2)                  ,
    dret_reversed_charge        decimal(7,2)                  ,
    dret_account_credit         decimal(7,2)                  ,
    dret_net_loss               decimal(7,2)                  ,
    primary key (dret_product_sk, dret_order_number)
);

create table digital_order_line
(
    dol_sold_date_sk           integer                       ,
    dol_sold_time_sk           integer                       ,
    dol_ship_date_sk           integer                       ,
    dol_product_sk                integer               not null,
    dol_bill_account_sk       integer                       ,
    dol_bill_profile_sk          integer                       ,
    dol_bill_household_sk          integer                       ,
    dol_bill_addr_sk           integer                       ,
    dol_ship_account_sk       integer                       ,
    dol_ship_profile_sk          integer                       ,
    dol_ship_household_sk          integer                       ,
    dol_ship_addr_sk           integer                       ,
    dol_page_sk            integer                       ,
    dol_site_sk            integer                       ,
    dol_delivery_method_sk           integer                       ,
    dol_fulfillment_site_sk           integer                       ,
    dol_campaign_sk               integer                       ,
    dol_order_number           integer               not null,
    dol_quantity               integer                       ,
    dol_wholesale_cost         decimal(7,2)                  ,
    dol_list_price             decimal(7,2)                  ,
    dol_sales_price            decimal(7,2)                  ,
    dol_ext_discount_amt       decimal(7,2)                  ,
    dol_ext_sales_price        decimal(7,2)                  ,
    dol_ext_wholesale_cost     decimal(7,2)                  ,
    dol_ext_list_price         decimal(7,2)                  ,
    dol_ext_tax                decimal(7,2)                  ,
    dol_coupon_amt             decimal(7,2)                  ,
    dol_ext_ship_cost          decimal(7,2)                  ,
    dol_net_paid               decimal(7,2)                  ,
    dol_net_paid_inc_tax       decimal(7,2)                  ,
    dol_net_paid_inc_ship      decimal(7,2)                  ,
    dol_net_paid_inc_ship_tax  decimal(7,2)                  ,
    dol_net_profit             decimal(7,2)                  ,
    primary key (dol_product_sk, dol_order_number)
);

create table assisted_order_line
(
    aol_sold_date_sk           integer                       ,
    aol_sold_time_sk           integer                       ,
    aol_ship_date_sk           integer                       ,
    aol_bill_account_sk       integer                       ,
    aol_bill_profile_sk          integer                       ,
    aol_bill_household_sk          integer                       ,
    aol_bill_addr_sk           integer                       ,
    aol_ship_account_sk       integer                       ,
    aol_ship_profile_sk          integer                       ,
    aol_ship_household_sk          integer                       ,
    aol_ship_addr_sk           integer                       ,
    aol_service_center_sk         integer                       ,
    aol_catalog_section_sk        integer                       ,
    aol_delivery_method_sk           integer                       ,
    aol_fulfillment_site_sk           integer                       ,
    aol_product_sk                integer               not null,
    aol_campaign_sk               integer                       ,
    aol_order_number           integer               not null,
    aol_quantity               integer                       ,
    aol_wholesale_cost         decimal(7,2)                  ,
    aol_list_price             decimal(7,2)                  ,
    aol_sales_price            decimal(7,2)                  ,
    aol_ext_discount_amt       decimal(7,2)                  ,
    aol_ext_sales_price        decimal(7,2)                  ,
    aol_ext_wholesale_cost     decimal(7,2)                  ,
    aol_ext_list_price         decimal(7,2)                  ,
    aol_ext_tax                decimal(7,2)                  ,
    aol_coupon_amt             decimal(7,2)                  ,
    aol_ext_ship_cost          decimal(7,2)                  ,
    aol_net_paid               decimal(7,2)                  ,
    aol_net_paid_inc_tax       decimal(7,2)                  ,
    aol_net_paid_inc_ship      decimal(7,2)                  ,
    aol_net_paid_inc_ship_tax  decimal(7,2)                  ,
    aol_net_profit             decimal(7,2)                  ,
    primary key (aol_product_sk, aol_order_number)
);

create table branch_order_line
(
    bol_sold_date_sk           integer                       ,
    bol_sold_time_sk           integer                       ,
    bol_product_sk                integer               not null,
    bol_account_sk            integer                       ,
    bol_profile_sk               integer                       ,
    bol_household_sk               integer                       ,
    bol_addr_sk                integer                       ,
    bol_branch_sk               integer                       ,
    bol_campaign_sk               integer                       ,
    bol_receipt_number          integer               not null,
    bol_quantity               integer                       ,
    bol_wholesale_cost         decimal(7,2)                  ,
    bol_list_price             decimal(7,2)                  ,
    bol_sales_price            decimal(7,2)                  ,
    bol_ext_discount_amt       decimal(7,2)                  ,
    bol_ext_sales_price        decimal(7,2)                  ,
    bol_ext_wholesale_cost     decimal(7,2)                  ,
    bol_ext_list_price         decimal(7,2)                  ,
    bol_ext_tax                decimal(7,2)                  ,
    bol_coupon_amt             decimal(7,2)                  ,
    bol_net_paid               decimal(7,2)                  ,
    bol_net_paid_inc_tax       decimal(7,2)                  ,
    bol_net_profit             decimal(7,2)                  ,
    primary key (bol_product_sk, bol_receipt_number)
);



-- Data Loading
COPY service_center FROM '/workload_data/call_center.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY catalog_section FROM '/workload_data/catalog_page.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY assisted_returns FROM '/workload_data/catalog_returns.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY assisted_order_line FROM '/workload_data/catalog_sales.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY shopper_account FROM '/workload_data/customer.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY account_address FROM '/workload_data/customer_address.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY account_profile FROM '/workload_data/customer_demographics.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY calendar_day FROM '/workload_data/date_dim.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY data_build_info FROM '/workload_data/dbgen_version.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY household_profile FROM '/workload_data/household_demographics.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY budget_band FROM '/workload_data/income_band.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY stock_snapshot FROM '/workload_data/inventory.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY product FROM '/workload_data/item.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY campaign FROM '/workload_data/promotion.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY return_reason FROM '/workload_data/reason.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY delivery_method FROM '/workload_data/ship_mode.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY branch FROM '/workload_data/store.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY branch_returns FROM '/workload_data/store_returns.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY branch_order_line FROM '/workload_data/store_sales.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY clock_time FROM '/workload_data/time_dim.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY fulfillment_site FROM '/workload_data/warehouse.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY digital_page FROM '/workload_data/web_page.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY digital_returns FROM '/workload_data/web_returns.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY digital_order_line FROM '/workload_data/web_sales.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');
COPY digital_site FROM '/workload_data/web_site.dat' WITH (FORMAT csv, DELIMITER '|', NULL '');


CREATE TABLE IF NOT EXISTS public.formtemplate_formdata
( id varchar(32) NOT NULL,
    sys_id integer NOT NULL,
    org_id integer NOT NULL,
    biz_id integer NOT NULL,
    src_id integer NOT NULL,
    field_01 varchar(1023),
    field_02 varchar(1023),
    field_03 varchar(1023),
    field_04 varchar(1023),
    field_05 varchar(1023),
    field_06 varchar(1023),
    field_07 varchar(1023),
    field_08 varchar(1023),
    field_09 varchar(1023),
    field_10 varchar(1023),
    field_11 varchar(1023),
    field_12 varchar(1023),
    field_13 varchar(1023),
    field_14 varchar(1023),
    field_15 varchar(1023),
    field_16 varchar(1023),
    field_17 varchar(1023),
    field_18 varchar(1023),
    field_19 varchar(1023),
    field_20 varchar(1023),
    field_21 varchar(1023),
    field_22 varchar(1023),
    field_23 varchar(1023),
    field_24 varchar(1023),
    field_25 varchar(1023),
    field_26 varchar(1023),
    field_27 varchar(1023),
    field_28 varchar(1023),
    field_29 varchar(1023),
    field_30 varchar(1023),
    field_31 varchar(1023),
    field_32 varchar(1023),
    field_33 varchar(1023),
    field_34 varchar(1023),
    field_35 varchar(1023),
    field_36 varchar(1023),
    field_37 varchar(1023),
    field_38 varchar(1023),
    field_39 varchar(1023),
    field_40 varchar(1023),
    field_41 varchar(1023),
    field_42 varchar(1023),
    field_43 varchar(1023),
    field_44 varchar(1023),
    field_45 varchar(1023),
    field_46 varchar(1023),
    field_47 varchar(1023),
    field_48 varchar(1023),
    field_49 varchar(1023),
    field_50 varchar(1023),
    date_01 date,
    date_02 date,
    date_03 date,
    date_04 date,
    date_05 date,
    date_06 date,
    date_07 date,
    date_08 date,
    date_09 date,
    date_10 date,
    datetime_01 timestamp with time zone,
    datetime_02 timestamp with time zone,
    datetime_03 timestamp with time zone,
    datetime_04 timestamp with time zone,
    datetime_05 timestamp with time zone,
    datetime_06 timestamp with time zone,
    datetime_07 timestamp with time zone,
    datetime_08 timestamp with time zone,
    datetime_09 timestamp with time zone,
    datetime_10 timestamp with time zone,
    int_01 bigint,
    int_02 bigint,
    int_03 bigint,
    int_04 bigint,
    int_05 bigint,
    int_06 bigint,
    int_07 bigint,
    int_08 bigint,
    int_09 bigint,
    int_10 bigint,
    float_01 numeric(16,4),
    float_02 numeric(16,4),
    float_03 numeric(16,4),
    float_04 numeric(16,4),
    float_05 numeric(16,4),
    float_06 numeric(16,4),
    float_07 numeric(16,4),
    float_08 numeric(16,4),
    float_09 numeric(16,4),
    float_10 numeric(16,4),
    department_id varchar(32),
    template_id varchar(32),
    user_id varchar(32),
    text_01 text,
    parent_id varchar(32),
    create_time timestamp with time zone NOT NULL,
    altitude double precision,
    latitude double precision,
    longitude double precision,
    obj_id varchar(32)
);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_altitude_de0a999c ON public.formtemplate_formdata (altitude);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_src_id_7cde581b ON public.formtemplate_formdata (src_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_obj_id ON public.formtemplate_formdata (obj_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_date_01_ef509f3c ON public.formtemplate_formdata (date_01);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_date_02_fc19ef3d ON public.formtemplate_formdata (date_02);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_datetime_01_e37e63b8 ON public.formtemplate_formdata (datetime_01);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_datetime_02_bf2a0635 ON public.formtemplate_formdata (datetime_02);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_department_id_8be36716 ON public.formtemplate_formdata (department_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_field_01_63aca99f ON public.formtemplate_formdata (field_01);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_field_02_4480ebe7 ON public.formtemplate_formdata (field_02);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_field_03_00638e6d ON public.formtemplate_formdata (field_03);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_field_04_167dfbdc ON public.formtemplate_formdata (field_04);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_field_05_bacc09bc ON public.formtemplate_formdata (field_05);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_float_01_fae2cdef ON public.formtemplate_formdata (float_01);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_float_02_c0c0814f ON public.formtemplate_formdata (float_02);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_int_01_b2130594 ON public.formtemplate_formdata (int_01);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_int_02_7cbc4e85 ON public.formtemplate_formdata (int_02);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_int_03_f512094d ON public.formtemplate_formdata (int_03);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_int_04_52a03eb7 ON public.formtemplate_formdata (int_04);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_int_05_fcb32915 ON public.formtemplate_formdata (int_05);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_latitude_a7524c2f ON public.formtemplate_formdata (latitude);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_longitude_272e2976 ON public.formtemplate_formdata (longitude);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_org_id_a9fa8da1 ON public.formtemplate_formdata (org_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_parent_id_0fee162e ON public.formtemplate_formdata (parent_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_pkey ON public.formtemplate_formdata (id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_sys_id_a3054cc2 ON public.formtemplate_formdata (sys_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_template_id_cc6f09e7 ON public.formtemplate_formdata (template_id);
CREATE INDEX IF NOT EXISTS formtemplate_formdata_user_id_dc1ededd ON public.formtemplate_formdata (user_id);

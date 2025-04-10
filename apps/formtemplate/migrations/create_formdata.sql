
DROP TABLE IF EXISTS public.formtemplate_formdata;
CREATE TABLE IF NOT EXISTS public.formtemplate_formdata
( id character varying(32) NOT NULL,
    sys_id integer NOT NULL,
    org_id integer NOT NULL,
    biz_id integer NOT NULL,
    src_id integer NOT NULL,
    field_01 character varying(1023),
    field_02 character varying(1023),
    field_03 character varying(1023),
    field_04 character varying(1023),
    field_05 character varying(1023),
    field_06 character varying(1023),
    field_07 character varying(1023),
    field_08 character varying(1023),
    field_09 character varying(1023),
    field_10 character varying(1023),
    field_11 character varying(1023),
    field_12 character varying(1023),
    field_13 character varying(1023),
    field_14 character varying(1023),
    field_15 character varying(1023),
    field_16 character varying(1023),
    field_17 character varying(1023),
    field_18 character varying(1023),
    field_19 character varying(1023),
    field_20 character varying(1023),
    field_21 character varying(1023),
    field_22 character varying(1023),
    field_23 character varying(1023),
    field_24 character varying(1023),
    field_25 character varying(1023),
    field_26 character varying(1023),
    field_27 character varying(1023),
    field_28 character varying(1023),
    field_29 character varying(1023),
    field_30 character varying(1023),
    field_31 character varying(1023),
    field_32 character varying(1023),
    field_33 character varying(1023),
    field_34 character varying(1023),
    field_35 character varying(1023),
    field_36 character varying(1023),
    field_37 character varying(1023),
    field_38 character varying(1023),
    field_39 character varying(1023),
    field_40 character varying(1023),
    field_41 character varying(1023),
    field_42 character varying(1023),
    field_43 character varying(1023),
    field_44 character varying(1023),
    field_45 character varying(1023),
    field_46 character varying(1023),
    field_47 character varying(1023),
    field_48 character varying(1023),
    field_49 character varying(1023),
    field_50 character varying(1023),
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
    department_id character varying(32),
    template_id character varying(32),
    user_id character varying(32),
    text_01 text,
    parent_id character varying(32),
    create_time timestamp with time zone NOT NULL,
    altitude double precision,
    latitude double precision,
    longitude double precision,
    obj_id character varying(32)
) PARTITION BY HASH (src_id);

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

CREATE TABLE public.formtemplate_formdata_part_0 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 0);
CREATE TABLE public.formtemplate_formdata_part_1 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 1);
CREATE TABLE public.formtemplate_formdata_part_2 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 2);
CREATE TABLE public.formtemplate_formdata_part_3 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 3);
CREATE TABLE public.formtemplate_formdata_part_4 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 4);
CREATE TABLE public.formtemplate_formdata_part_5 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 5);
CREATE TABLE public.formtemplate_formdata_part_6 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 6);
CREATE TABLE public.formtemplate_formdata_part_7 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 7);
CREATE TABLE public.formtemplate_formdata_part_8 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 8);
CREATE TABLE public.formtemplate_formdata_part_9 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 9);
CREATE TABLE public.formtemplate_formdata_part_10 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 10);
CREATE TABLE public.formtemplate_formdata_part_11 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 11);
CREATE TABLE public.formtemplate_formdata_part_12 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 12);
CREATE TABLE public.formtemplate_formdata_part_13 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 13);
CREATE TABLE public.formtemplate_formdata_part_14 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 14);
CREATE TABLE public.formtemplate_formdata_part_15 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 15);
CREATE TABLE public.formtemplate_formdata_part_16 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 16);
CREATE TABLE public.formtemplate_formdata_part_17 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 17);
CREATE TABLE public.formtemplate_formdata_part_18 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 18);
CREATE TABLE public.formtemplate_formdata_part_19 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 19);
CREATE TABLE public.formtemplate_formdata_part_20 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 20);
CREATE TABLE public.formtemplate_formdata_part_21 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 21);
CREATE TABLE public.formtemplate_formdata_part_22 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 22);
CREATE TABLE public.formtemplate_formdata_part_23 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 23);
CREATE TABLE public.formtemplate_formdata_part_24 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 24);
CREATE TABLE public.formtemplate_formdata_part_25 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 25);
CREATE TABLE public.formtemplate_formdata_part_26 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 26);
CREATE TABLE public.formtemplate_formdata_part_27 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 27);
CREATE TABLE public.formtemplate_formdata_part_28 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 28);
CREATE TABLE public.formtemplate_formdata_part_29 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 29);
CREATE TABLE public.formtemplate_formdata_part_30 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 30);
CREATE TABLE public.formtemplate_formdata_part_31 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 31);
CREATE TABLE public.formtemplate_formdata_part_32 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 32);
CREATE TABLE public.formtemplate_formdata_part_33 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 33);
CREATE TABLE public.formtemplate_formdata_part_34 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 34);
CREATE TABLE public.formtemplate_formdata_part_35 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 35);
CREATE TABLE public.formtemplate_formdata_part_36 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 36);
CREATE TABLE public.formtemplate_formdata_part_37 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 37);
CREATE TABLE public.formtemplate_formdata_part_38 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 38);
CREATE TABLE public.formtemplate_formdata_part_39 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 39);
CREATE TABLE public.formtemplate_formdata_part_40 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 40);
CREATE TABLE public.formtemplate_formdata_part_41 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 41);
CREATE TABLE public.formtemplate_formdata_part_42 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 42);
CREATE TABLE public.formtemplate_formdata_part_43 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 43);
CREATE TABLE public.formtemplate_formdata_part_44 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 44);
CREATE TABLE public.formtemplate_formdata_part_45 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 45);
CREATE TABLE public.formtemplate_formdata_part_46 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 46);
CREATE TABLE public.formtemplate_formdata_part_47 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 47);
CREATE TABLE public.formtemplate_formdata_part_48 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 48);
CREATE TABLE public.formtemplate_formdata_part_49 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 49);
CREATE TABLE public.formtemplate_formdata_part_50 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 50);
CREATE TABLE public.formtemplate_formdata_part_51 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 51);
CREATE TABLE public.formtemplate_formdata_part_52 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 52);
CREATE TABLE public.formtemplate_formdata_part_53 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 53);
CREATE TABLE public.formtemplate_formdata_part_54 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 54);
CREATE TABLE public.formtemplate_formdata_part_55 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 55);
CREATE TABLE public.formtemplate_formdata_part_56 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 56);
CREATE TABLE public.formtemplate_formdata_part_57 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 57);
CREATE TABLE public.formtemplate_formdata_part_58 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 58);
CREATE TABLE public.formtemplate_formdata_part_59 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 59);
CREATE TABLE public.formtemplate_formdata_part_60 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 60);
CREATE TABLE public.formtemplate_formdata_part_61 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 61);
CREATE TABLE public.formtemplate_formdata_part_62 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 62);
CREATE TABLE public.formtemplate_formdata_part_63 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 63);
CREATE TABLE public.formtemplate_formdata_part_64 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 64);
CREATE TABLE public.formtemplate_formdata_part_65 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 65);
CREATE TABLE public.formtemplate_formdata_part_66 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 66);
CREATE TABLE public.formtemplate_formdata_part_67 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 67);
CREATE TABLE public.formtemplate_formdata_part_68 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 68);
CREATE TABLE public.formtemplate_formdata_part_69 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 69);
CREATE TABLE public.formtemplate_formdata_part_70 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 70);
CREATE TABLE public.formtemplate_formdata_part_71 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 71);
CREATE TABLE public.formtemplate_formdata_part_72 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 72);
CREATE TABLE public.formtemplate_formdata_part_73 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 73);
CREATE TABLE public.formtemplate_formdata_part_74 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 74);
CREATE TABLE public.formtemplate_formdata_part_75 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 75);
CREATE TABLE public.formtemplate_formdata_part_76 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 76);
CREATE TABLE public.formtemplate_formdata_part_77 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 77);
CREATE TABLE public.formtemplate_formdata_part_78 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 78);
CREATE TABLE public.formtemplate_formdata_part_79 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 79);
CREATE TABLE public.formtemplate_formdata_part_80 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 80);
CREATE TABLE public.formtemplate_formdata_part_81 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 81);
CREATE TABLE public.formtemplate_formdata_part_82 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 82);
CREATE TABLE public.formtemplate_formdata_part_83 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 83);
CREATE TABLE public.formtemplate_formdata_part_84 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 84);
CREATE TABLE public.formtemplate_formdata_part_85 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 85);
CREATE TABLE public.formtemplate_formdata_part_86 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 86);
CREATE TABLE public.formtemplate_formdata_part_87 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 87);
CREATE TABLE public.formtemplate_formdata_part_88 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 88);
CREATE TABLE public.formtemplate_formdata_part_89 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 89);
CREATE TABLE public.formtemplate_formdata_part_90 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 90);
CREATE TABLE public.formtemplate_formdata_part_91 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 91);
CREATE TABLE public.formtemplate_formdata_part_92 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 92);
CREATE TABLE public.formtemplate_formdata_part_93 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 93);
CREATE TABLE public.formtemplate_formdata_part_94 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 94);
CREATE TABLE public.formtemplate_formdata_part_95 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 95);
CREATE TABLE public.formtemplate_formdata_part_96 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 96);
CREATE TABLE public.formtemplate_formdata_part_97 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 97);
CREATE TABLE public.formtemplate_formdata_part_98 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 98);
CREATE TABLE public.formtemplate_formdata_part_99 PARTITION OF public.formtemplate_formdata FOR VALUES WITH (MODULUS 100, REMAINDER 99);

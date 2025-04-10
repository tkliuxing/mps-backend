from rest_framework.serializers import ModelSerializer
from . import models


class AccountSerializer(ModelSerializer):

    class Meta:
        model = models.Account
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'user',
            'obj_id',
            'acc_1_name',
            'acc_1_type',
            'acc_1_balance',
            'acc_1_lock',
            'acc_2_name',
            'acc_2_type',
            'acc_2_balance',
            'acc_2_lock',
            'acc_3_name',
            'acc_3_type',
            'acc_3_balance',
            'acc_3_lock',
            'jifen_acc',
            'jifen_balance',
            'create_time',
            'update_time',
        )
        read_only_fields = [
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'user', 'obj_id',
            'acc_1_type', 'acc_1_balance', 'acc_1_lock',
            'acc_2_type', 'acc_2_balance', 'acc_2_lock',
            'acc_3_type', 'acc_3_balance', 'acc_3_lock',
            'jifen_balance',
            'create_time',
            'update_time',
        ]


class AccountCreateSerializer(ModelSerializer):

    class Meta:
        model = models.Account
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'user',
            'obj_id',
            'acc_1_name',
            'acc_1_type',
            'acc_1_balance',
            'acc_1_lock',
            'acc_2_name',
            'acc_2_type',
            'acc_2_balance',
            'acc_2_lock',
            'acc_3_name',
            'acc_3_type',
            'acc_3_balance',
            'acc_3_lock',
            'jifen_acc',
            'jifen_balance',
            'create_time',
            'update_time',
        )
        read_only_fields = [
            'acc_1_balance', 'acc_1_lock',
            'acc_2_balance', 'acc_2_lock',
            'acc_3_balance', 'acc_3_lock',
            'jifen_balance',
            'create_time',
            'update_time',
        ]


class AccountStatementsSerializer(ModelSerializer):

    class Meta:
        model = models.AccountStatements
        fields = (
            'pk',
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'acc',
            'acc_name',
            'record_type',
            'amount',
            'used_amount',
            'end_time',
            'order_num',
            'tpp_name',
            'tpp_no',
            'tpp_desc',
            'desc',
            'create_time',
            'update_time',
            'is_end',
            'field_01',
            'field_02',
            'field_03',
            'field_04',
            'field_05',
            'float_01',
            'float_02',
            'float_03',
            'float_04',
            'float_05',
        )
        read_only_fields = [
            'sys_id',
            'org_id',
            'biz_id',
            'src_id',
            'acc',
            'acc_name',
            'record_type',
            'amount',
            'used_amount',
            'end_time',
            'desc',
            'create_time',
            'update_time',
            'tpp_name',
            'tpp_no',
            'order_num',
        ]

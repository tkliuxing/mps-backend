from django.db import models

from utility.db_fields import TableNamePKField


class MailBox(models.Model):
    CATEGORYS = (
        ('mailbox', 'mailbox', ),
        ('notice', 'notice', ),
    )
    id = TableNamePKField('mb')
    category = models.CharField(
        '消息类型', max_length=8, choices=CATEGORYS, default='notice', help_text='消息类型'
    )
    msg_type = models.ForeignKey(
        'baseconfig.BaseTree', on_delete=models.CASCADE, null=True, blank=True, help_text='消息分类',
        db_constraint=False, related_name='+'
    )
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    obj_id = models.CharField('关联对象ID', max_length=64, null=True, blank=True, help_text='关联对象ID')
    obj_type = models.CharField('关联对象类型', max_length=64, null=True, blank=True, help_text='关联对象类型')
    title = models.CharField('标题', max_length=255, null=True, blank=True, help_text='标题')
    content = models.TextField('内容', null=True, blank=True, help_text='内容')
    is_published = models.BooleanField('已发布', default=True, help_text='已发布')
    publish_date = models.DateField('发布日期', null=True, blank=True, help_text='发布日期')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, help_text='创建时间')
    last_modify = models.DateTimeField('最后修改时间', auto_now=True, help_text='最后修改时间')
    is_read = models.BooleanField('已读', default=False, help_text='已读')
    user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL,
        null=True, blank=True, help_text='接收用户ID', db_constraint=False,
        related_name='+', verbose_name='接收用户'
    )
    from_user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL,
        null=True, blank=True, help_text='发送用户ID', db_constraint=False,
        related_name='+', verbose_name='发送用户'
    )
    is_public = models.BooleanField('全局公开', default=True, help_text='全局公开[false为部分公开，须填写public_user]')
    public_user = models.ManyToManyField(
        'usercenter.User', blank=True, related_name='own_notices', verbose_name='公开范围', help_text='公开范围', db_constraint=False
    )
    departments = models.ManyToManyField(
        'usercenter.Department', blank=True, related_name='notices',
        verbose_name='部门范围', help_text='部门范围', db_constraint=False
    )
    department_range = models.CharField(
        '部门公布范围', choices=(('本级', '本级'), ('本级及以下', '本级及以下')),
        max_length=32, null=True, blank=True, help_text='部门范围'
    )

    class Meta:
        verbose_name = '01.通知'
        verbose_name_plural = verbose_name
        ordering = ('-create_time', 'user_id',)

    def __str__(self):
        return "{} {}".format(self.pk, self.title)

    @classmethod
    def new_mail(cls, title, content, user, from_user=None):
        return cls.objects.create(
            title=title, content=content, user=user, from_user=from_user,
            category='mailbox',
        )


class NoticePool(models.Model):
    '''
    通知池
    '''
    id = TableNamePKField('np')
    sys_id = models.IntegerField('系统ID', default=1, db_index=True)
    org_id = models.IntegerField('组织ID', default=1, db_index=True)
    biz_id = models.IntegerField('业务ID', default=1, db_index=True)
    src_id = models.IntegerField('数据源ID', default=1, db_index=True)
    obj_id = models.CharField('关联对象ID', max_length=64, null=True, blank=True, help_text='关联对象ID', db_index=True)
    obj_type = models.CharField('关联对象类型', max_length=64, null=True, blank=True, help_text='关联对象类型', db_index=True)
    msg_type = models.ForeignKey(
        'baseconfig.BaseTree', on_delete=models.CASCADE, null=True, blank=True, help_text='消息分类',
        db_constraint=False, related_name='+'
    )
    title = models.CharField('标题', max_length=255, null=True, blank=True, help_text='标题')
    content = models.TextField('内容', null=True, blank=True, help_text='内容')
    send_time = models.DateTimeField('发送时间', null=True, blank=True, help_text='发送时间', db_index=True)
    is_circulation = models.BooleanField('循环发送', default=False, help_text='循环发送')
    circulation_time = models.DurationField('循环时间', null=True, blank=True, help_text='循环时间')
    is_sent = models.BooleanField('已发送', default=False, help_text='已发送', db_index=True)
    from_user = models.ForeignKey(
        'usercenter.User', on_delete=models.SET_NULL,
        null=True, blank=True, help_text='发送用户ID', db_constraint=False,
        related_name='+', verbose_name='发送用户'
    )
    from_user_display = models.CharField('发送用户', max_length=64, null=True, blank=True, help_text='发送用户')
    send_to = models.ManyToManyField(
        'usercenter.User', blank=True, related_name='notice_pool',
        verbose_name='发送对象', help_text='发送对象', db_constraint=False
    )
    is_public = models.BooleanField('全局公开', default=False, help_text='全局公开[false为部分公开，须填写send_to]')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, help_text='创建时间')
    last_modify = models.DateTimeField('最后修改时间', auto_now=True, help_text='最后修改时间')
    error_message = models.TextField('错误信息', null=True, blank=True, help_text='错误信息')

    departments = models.ManyToManyField(
        'usercenter.Department', blank=True, related_name='+',
        verbose_name='部门范围', help_text='部门范围', db_constraint=False
    )
    department_range = models.CharField(
        '部门公布范围', choices=(('本级', '本级'), ('本级及以下', '本级及以下')),
        max_length=32, null=True, blank=True, help_text='部门范围'
    )

    # 发送渠道
    CHANNELS = (
        ('email', 'email', ),
        ('sms', '短信', ),
        ('wxa', '微信小程序'),
        ('mailbox', '站内信'),
    )
    channel = models.CharField(
        '发送渠道', max_length=16, choices=CHANNELS, default='mailbox', help_text='发送渠道'
    )

    class Meta:
        verbose_name = '02.通知池'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "02.通知池: {}".format(self.pk)

    def do_circulation(self):
        if self.is_circulation and self.circulation_time and self.send_time:
            self.send_time = self.send_time + self.circulation_time
            self.is_sent = False
            self.save()

    def send_wxa(self):
        pass

    def send_mailbox(self):
        if self.send_to:
            for user in self.send_to.all():
                MailBox.objects.create(
                    sys_id=self.sys_id, org_id=self.org_id, biz_id=self.biz_id,
                    src_id=self.src_id, obj_id=self.obj_id, obj_type=self.obj_type,
                    title=self.title, content=self.content, from_user=self.from_user,
                    user=user, category='mailbox', msg_type=self.msg_type,
                )

    def send_sms(self):
        from .tasks import send_sms
        send_sms.delay(self.pk)

    def send_email(self):
        from .tasks import send_email
        try:
            send_email(self)
        except Exception as e:
            self.is_sent = False
            self.error_message = str(e)
            self.save()
            raise e

    def send(self):
        if self.is_sent:
            return
        if self.channel == 'email':
            # 发送邮件
            self.send_email()
        elif self.channel == 'wxa':
            # 发送微信
            self.send_wxa()
        elif self.channel == 'sms':
            # 发送短信
            self.send_sms()
        elif self.channel == 'mailbox':
            # 发送站内信
            self.send_mailbox()
        else:
            pass
        self.is_sent = True
        self.save()
        self.do_circulation()

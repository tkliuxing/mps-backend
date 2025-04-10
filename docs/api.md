# API 说明文档


## 概念说明

API接口是对域名后访问路径对应功能的说明，请求地址的一般格式为 `https://域名/api/v1/接口名/query参数` ，`必须填写路径最后的 /`

线上项目一般具有在线API结构文档，地址为： `https://域名/api-docs/`，登录后才可查看。

本文档不列出所有接口的字段和参数，只列明接口定义和功能说明，具体数据结构和参数请以线上实际接口文档为准。

API请求一般需在请求头中具备令牌才可访问，特殊情况会做出说明。

## 请求类型

通常接口可接收六种类型的请求：
* `GET` 查询列出
* `POST` 新增
* `PUT` 修改（全字段）
* `PATCH` 修改（部分字段）
* `DELETE` 删除
* `OPTION` 获取数据结构

其中 `GET` 请求分为两种，分别对应不同路径，请求结果具有不同的数据结构：
* `接口名/` 代表列出该接口下数据，通常具有查询参数和分页参数，返回结果根据是否分页决定数据结构，一般为数组形式；
* `接口名/对象ID/` 代表获取指定ID的对象，数据结构一般为对象形式。


## 系统基础接口

* `system` 系统定义接口，定义全局 `sys_id` 所关联的系统信息
* `smsconfig` 系统短信平台配置接口
* `smslog` 短信发送记录只读接口，**仅GET**
* `permissions` 权限定义接口
* `group` 角色定义接口
* `baseconfigcategory` 基础类别接口，用来管理基础配置分类
* `baseconfigcategorynamed` 基础类别接口，根据name而不是PK获取基础类别详情
* `baseconfigitem` 基础配置项定义接口
* `baseconfigvalue` 基础配置项值接口
* `basetree` 分类树树形接口
* `flatbasetree` 分类树平铺接口
* `basetreemove` 分类树节点移动接口，**仅POST**
* `baseconfigfileupload` 通用文件上传接口，**仅POST**
* `captcha` 图形验证码获取接口，**仅POST**


## 用户相关接口

* `auth` 用户令牌获取接口，通过用户名和密码获取授权令牌
* `phoneauth` 手机登录接口第一步，发送验证码接口，**仅POST**
* `phonelogin` 手机登录接口第二步，通过验证码和手机号获取授权令牌
* `user` 系统登录用户接口，进行对用户的增删查改
* `userrequirecreate` 系统登录用户注册申请接口（仅创建），用来进行用户注册申请，可 **无令牌访问**
* `userrequire` 系统登录用户注册申请接口，一般用来作为查询类操作和审核不通过操作使用
* `userrequirepass` 系统登录用户注册申请审核通过接口，审核通过操作需访问此接口，**仅PUT和PATCH操作**
* `userloginlog` 用户登录日志只读接口，**仅GET**
* `userorder` 系统登录用户排序接口
* `changepwd` 当前用户密码修改接口，**仅POST**
* `myinfo` 当前用户基本信息读取接口，**仅GET**


* `department` 部门树形接口
* `flatdepartment` 部门平铺接口
* `departmentmove` 部门排列移动接口，**仅POST**


## 消息通知类接口

* `notice` 通知公告接口
* `view-my-notice` 当前用户查看通知公告接口，**仅GET**
* `mailbox` 用户站内信接口
* `mailbox-unread-count` 用户未读站内信数接口，**仅GET**
* `mailbox-mark-all-read` 标记所有站内信为已读接口，**仅POST**


## 业务数据接口

### 不定类型数据

* `formdatadefine` 表单数据源定义接口
* `formfields` 表单字段定义接口
* `formtemplate` 表单模板定义接口
* `formtemplatecopy` 表单模板定义 Copy 接口，**仅POST**
* `formdata` 表单数据接口
* `formdatareportconf` 数据报表定义接口
* `formdatareport` 数据报表读取接口，**仅GET**

### 特定类型数据

* `goods` 物品类接口
* `services` 服务类接口
* `org` 组织机构类接口
* `customer` 人员类接口

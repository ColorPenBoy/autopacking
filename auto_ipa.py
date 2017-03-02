#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time, hashlib, smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

#######################################################################
# 注意事项：
# 1、打包时，必须进入项目根目录
# 2、生成archive包时，使用证书、描述文件UUID
# 3、生成ipa包时，使用描述文件（描述文件名称）

#######################################################################
# 当前文件目录
current_file_path = os.getcwd()
# 桌面目录
desktop_path = os.path.expanduser('~') + '/Desktop'

#######################################################################
# 项目根目录
project_path = current_file_path
# archive包存储路径
archive_path = current_file_path + "/build/XXXXXX.xcarchive"
# ipa包存储路径
targerIPA_parth = current_file_path + "/build"
# 中间文件生成的路径 - 可以不指定
configuration_build_dir = current_file_path + "/build"
# 存储 exportOptionsPlist 路径
exports_plist_path = current_file_path + "/buildOptionPlist/AdHocExportOptions.plist"

# fir 的api token
fir_api_token = "your fir aip token"
# 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
fir_local_path = os.path.expanduser('~') + "/.rvm/rubies/ruby-2.0.0-p598/bin/fir"

#######################################################################
# 发送邮件的邮箱账号 - 打包者邮箱
mail_from_address = "your email address"
# 发送邮件的邮箱密码
mail_password = "your email password"
# 发送邮件邮箱的邮件服务器
mail_smtp_server = "smtp.163.com"
# 测试部门测试接收打包完成信息的邮箱
mail_to_address = "test email address"
# 抄送邮箱（邮箱之间";"分隔，不能有空格）
mail_copy_to_address = "test email address"

#######################################################################
# 项目名称
project_name = "XXXXXX"

# 编译环境：1、Release  2、Debug  3、Release Adhoc
configurationType = "Debug"

# SDK名称
SDK = "iphoneos"

# 证书名称(注意引号)
code_sign_identity = "'your certificate name'"

# 描述文件名称provisioning profile UUID
# 获取途径 /Users/user admin/Library/MobileDevice/Provisioning Profiles/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx.mobileprovision
# 也可以使用其它方式获取对应 .mobileprovision 的 UUID
provisioning_profile_UUID = "'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx'"

# 描述文件名称provisioning profile name
# 获取途径 从 development.apple.com 开发者中心对应的 provisioning profile 文件的名字。
# 如：xxx.mobileprovision ，去掉文件后缀
provisioning_profile_name = "xxx"

#######################################################################

# 从当前项目下，svn update
def project_svn_update():
    print("**************** subversion update project ****************")
    os.system('cd %s; svn upgrade; svn update' % project_path)

# 清理项目 创建build目录
def clean_project_mkdir_build():
    print("**************** start clean project ****************")
    os.system('cd %s;xcodebuild clean' % project_path) # clean 项目
    os.system('cd %s;rm -rf build' % project_path) # 删除旧build文件夹
    os.system('cd %s;mkdir build' % project_path) # 生成一个新build文件夹

# 生成archive文件，并清除以前的编辑
def build_project():
    print("**************** start build Debug ****************")
    os.system ('xcodebuild -list')
    os.system ('cd %s;xcodebuild -project XXXXXX.xcodeproj -scheme XXXXXX -configuration %s archive -archivePath %s CONFIGURATION_BUILD_DIR=%s CODE_SIGN_IDENTITY=%s PROVISIONING_PROFILE=%s'%(project_path, configurationType, archive_path, configuration_build_dir, code_sign_identity, provisioning_profile_UUID))
   
# app打包成IPA并签名，保存在指定目录
def build_ipa():
    print("**************** 开始打包IPA ****************")
    global ipa_filename
    ipa_filename = time.strftime('XXXXXX_%Y-%m-%d-%H-%M-%S.ipa',time.localtime(time.time()))
    os.system ('xcodebuild -exportArchive -exportFormat IPA -archivePath %s -exportPath %s/%s -exportProvisioningProfile %s' % (archive_path, targerIPA_parth, ipa_filename, provisioning_profile_name))

    # os.system ('xcodebuild -exportArchive -exportFormat IPA -archivePath %s -exportPath %s/%s -exportProvisioningProfile %s'%(archive_path, targerIPA_parth, ipa_filename, provisioning_profile_name))
    ####  xcrun xcodebuild -help 最下方 查看 exportOptionsPlist 可以写入的键值对
    ####  exportOptionsPlist 方法出现Apple 的 bug Error Domain=IDEDistributionErrorDomain Code=14 "No applicable devices found." 暂时不能用，只能使用旧API

# 上传到 FTP 服务器固定路径
def upload_fir():
    print("**************** 开始上传 ****************")
    if os.path.exists("%s/%s" % (targerIPA_parth,ipa_filename)):
        print("**************** 上传中，请稍后... ****************")
        ret = os.system("%s p '%s/%s' -T '%s'" % (fir_local_path, targerIPA_parth,ipa_filename,fir_api_token))
    else:
        print("**************** 没有找到ipa文件 ****************")

# 格式化邮件地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发邮件
def send_mail():
    print("**************** 开始发送邮件 ****************")
    msg = MIMEText('淘车通 iOS测试项目已经打包完毕，请前往 http://fir.im/tctc 下载测试！', 'plain', 'utf-8')
    msg['From'] = _format_addr('自动打包系统 <%s>' % mail_from_address)
    msg['To'] = _format_addr('测试人员 <%s>' % mail_to_address)
    msg['CC'] = _format_addr('相关人员 <%s>' % mail_copy_to_address)
    msg['Subject'] = Header('Color Pen iOS客户端打包程序', 'utf-8').encode()
    server = smtplib.SMTP(mail_smtp_server, 25)
    server.set_debuglevel(1)
    server.login(mail_from_address, mail_password)
    server.sendmail(mail_from_address, [mail_to_address], msg.as_string())
    server.quit()

def main():

    # SVN更新代码
    project_svn_update()
    # 清理并创建build目录
    clean_project_mkdir_build()
    # 编译coocaPods项目文件并 执行编译目录
    build_project()
    # 打包ipa 并制定到桌面
    build_ipa()
    # 上传fir
    upload_fir()
    # 发邮件
    send_mail()

# 执行
main()

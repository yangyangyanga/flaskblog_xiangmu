# 导入相关扩展类库
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class

# 创建相关扩展对象
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
login_manager = LoginManager()
photo = UploadSet('photos', IMAGES)

# 配置函数
def config_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    # 会话信息保护级别：
    # None：不使用，
    # 'basic'：基本级别，
    # 'strong'：用户信息更改立即退出
    login_manager.session_protection = 'strong'
    # 设置登录页面端点，当用户访问需要登录才能访问的页面，
    # 此时还没有登录，会自动跳转到此处
    login_manager.login_view = 'user.login'
    # 设置提醒信息，默认是英文提示信息
    login_manager.login_message = '需要登录才能访问'

    # 文件上传配置
    configure_uploads(app, photo)
    patch_request_class(app, size=None)

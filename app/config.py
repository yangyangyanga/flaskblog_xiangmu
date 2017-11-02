import os

base_uri = os.path.abspath(os.path.dirname(__file__))

# 通用配置
class Config:
    # 密钥，禁止使用中文
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'yangyang'
    # 数据库操作
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.163.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'yangyangyang_50055@163.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '19960427yyx'

    # 使用本地库中的bootstrap依赖包
    BOOTSTRAP_SERVE_LOCAL = True

    # 上传文件配置
    MAX_CONTENT_LENGTH = 1024 * 1024 * 16
    UPLOADED_PHOTOS_DEST = os.path.join(base_uri, 'static/upload')

    # 初始化的方法
    @staticmethod
    def init_app(app):
        pass

# 开发环境配置
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_uri, 'blog-dev.sqlite')

# 测试环境配置
class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_uri, 'blog-test.sqlite')

# 生产环境配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_uri, 'blog.sqlite')

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    # 默认配置
    'default': DevelopmentConfig,
}
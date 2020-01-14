#coding=utf-8
import pymysql
from common.configer import configer
from common.log import logger


class OperateMySQL():

    def __init__(self, db):
        cfg = configer.getconfiger('base.ini')
        try:
            self.env = db
            self.host = cfg.get(db, 'host')
            self.port = int(cfg.get(db, 'port'))
            self.user = cfg.get(db, 'user')
            self.passwd = cfg.get(db, 'passwd')
            try:
                self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd)
                logger.debug('The connection to the mysql environment: %s was successful' % db)
            except Exception:
                logger.exception('Failed to connect to the mysql environment: %s' % self.env)
        except Exception:
            logger.exception('Error retrieving configuration information from configuration file')


    def query_data(self, sql):
        cursor = self.conn.cursor()
        logger.info('Execute SQL statement: %s' % sql)
        try:
            cursor.execute(sql)
            ret = cursor.fetchall()
            return ret
        except Exception:
            logger.exception('Unable to fetch data')
        finally:
            cursor.close()

    # def modify_data(self, sql):
    #     logger.info('Execute SQL statement: %s' % sql)
    #     try:
    #         self.cursor.execute(sql)
    #         self.conn.commit()
    #     except Exception:
    #         self.conn.rollback()

    def close(self):
        try:
            self.conn.close()
            logger.debug('Connection closed successfully, %s' % self.env)
        except Exception:
            logger.exception('Failed to close connection, %s' % self.env)


if __name__ == '__main__':
    o = OperateMySQL('reg1')
    print(o.query_data("select * from jjxt.apply_photo_check")[0])
    o.close()

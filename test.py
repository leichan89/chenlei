import MySQLdb
import time
import datetime


class QueryCustomerQuestionData:

    def _conn_mysql_info(self):

        info = {
            'online3306': ['mysql-slave.h.highso.com.cn', 3306, 'prod-study-read', 'ZJ6uzYpVoPtI'],
            'online3307': ['mysql-slave.h.highso.com.cn', 3307, 'prod-study-read', 'ZJ6uzYpVoPtI'],
            'online3330': ['mysql-slave.h.highso.com.cn', 3330, 'prod-study-read', 'ZJ6uzYpVoPtI']
        }

        return info

    def cursor(self, mysql_info, db):

        info = self._conn_mysql_info()

        if mysql_info in info.keys():
            host = info[mysql_info][0]
            port = info[mysql_info][1]
            user = info[mysql_info][2]
            password = info[mysql_info][3]
            conn = MySQLdb.connect(host=host, port=port, user=user, password=password, db=db)
            cursor = conn.cursor()
            return cursor
        else:
            print('key值错误')


    def execsql(self, cursor, sql):
        cursor.execute(sql)
        return cursor.fetchall()

    def _datetime2timestamp(self, dt, to11=False):
        timetuple = dt.timetuple()
        second = time.mktime(timetuple)
        if to11:
            return int(second)
        microsecond = int(second * 1000 + dt.microsecond / 1000)
        return microsecond

    def _is_max_date(self, time1, time2, ismax=True):
        """
        比较两个时间段的大小
        :param time1:
        :param time2:
        :param ismax:
        :return:
        """
        if self._datetime2timestamp(time1) > self._datetime2timestamp(time2):
            max_time = time1
            min_time = time2
        else:
            max_time = time2
            min_time = time1
        if ismax:
            return max_time
        else:
            return min_time


    def _to_datetime(self, strdatetime):
        """
        字符串转datetime
        :param strdatetime:
        :return:
        """
        return datetime.datetime.strptime(strdatetime, "%Y-%m-%d %H:%M:%S")

    def cusormer_goods_type(self, goodsId, cursor_3306_highso):
        # 查询指定商品关联的类别和科目信息
        category_subject_id_list = f"SELECT DISTINCT g.categoryId, gs.subjectId FROM goodssubject as gs " \
            f"LEFT JOIN goods AS g ON gs.goodsId = g.id WHERE g.id = {goodsId}"

        query_question_info = q.execsql(cursor_3306_highso, category_subject_id_list)
        print(f"指定商品的类别和科目信息：{query_question_info}")
        return query_question_info


    def query_custormer_question_time(self, cursor_3306_highso, customerId, goodsId, query_start_time, query_end_time):
        """
        获取学员指定商品的有效期，并检查与查询时间是否存在交集，如果存在交集，则取交集的起止时间段作为查询条件
        在做题详情表中查询做题信息
        :param customerId:
        :param goodsId:
        :return:
        """

        query_start_time = self._to_datetime(query_start_time)
        query_end_time = self._to_datetime(query_end_time)

        query_custormer_service_time_sql = f"SELECT serviceStartTime, serviceEndTime, serviceCloseDate FROM customergoods " \
            f"WHERE goodsId={goodsId} AND customerId={customerId} LIMIT 1"

        query_custormer_service_time = q.execsql(cursor_3306_highso, query_custormer_service_time_sql)
        if not query_custormer_service_time:
            raise Exception(f"学员:{customerId}没有购买该商品:{goodsId}\n{query_custormer_service_time_sql}")
        starttime = query_custormer_service_time[0][0]
        serviceEndTime = query_custormer_service_time[0][1]
        serviceCloseDate = query_custormer_service_time[0][2]

        endtime = self._is_max_date(serviceCloseDate, serviceEndTime)

        print(f'学员的商品的起止时间：{starttime}---{endtime}')

        if self._datetime2timestamp(query_end_time) < self._datetime2timestamp(starttime) or \
                self._datetime2timestamp(query_start_time) > self._datetime2timestamp(endtime):
            raise Exception("查询时间与学员服务有效期时间没有交集")

        query_question_start_time = self._is_max_date(starttime, query_start_time)
        query_question_end_time = self._is_max_date(endtime, query_end_time, ismax=False)
        print(f"在做题详情表中的查询的时间段（学员服务有效期和查询时间段的交集）{str(query_question_start_time)}---{str(query_question_end_time)}")
        return (str(query_question_start_time), str(query_question_end_time))


    def question_sum(self, custormerid, start_time, end_time, cursor_3330_examlog, cursor_3306_exam, categoryId=None, subjectIds=None):
        """
        根据学员做题的类别或者类别+科目，查询指定时间段内的做题量数据，返回主观题和客观题做题量
        :param custormerid:
        :param start_time:
        :param end_time:
        :param cursor_3330_examlog:
        :param cursor_3306_exam:
        :return:
        """

        # 主观题
        answer_type = []
        # 客观题
        not_answer_type = []
        all_question_id = []
        table_sql = f'question_record_detail_{custormerid % 200}'

        # 目前精进后台学员管理-活跃数据没有去重做题量，加上了主观题的做题量
        question_id_sql = f"select distinct(question_id) from {table_sql} where customer_id={custormerid}" \
            f" and create_date between '{start_time}' and '{end_time}'"
        question_ids = self.execsql(cursor_3330_examlog, question_id_sql)

        # 不去重查询
        # question_id_sql = f"select question_id from {table_sql} where customer_id={custormerid}" \
        #     f" and create_date between '{start_time}' and '{end_time}'"
        # question_ids = self.execsql(cursor_3330_examlog, question_id_sql)
        # print(f"不去重查询sql:{question_id_sql}")
        # print(f"不去重查询的结果：{len(question_ids)}")

        if not question_ids:
            return None
        for r in question_ids:
            all_question_id.append(str(r[0]))

        # 目前精进后台没有去重，如果不去重，这里就需要遍历每个试题ID
        # 需要过滤删除了试题，且试题状态是Checked
        examType_sql = f"select id, examType from examquestion where id in ({','.join(all_question_id)}) and deleted=0 " \
            f"and examStatus='Checked'"

        if categoryId and not subjectIds:
            add_sql = f' and categoryId={categoryId}'
            examType_sql = examType_sql + add_sql
        if categoryId and subjectIds:
            add_sql = f' and categoryId={categoryId} and subjectId in ({",".join(subjectIds)})'
            examType_sql = examType_sql + add_sql

        all_question_type = q.execsql(cursor_3306_exam, examType_sql)

        for question_type in all_question_type:
            # AnswerQuestion简答题，FillInTheBlank填空题
            if question_type[1] == 'AnswerQuestion' or question_type[1] == 'FillInTheBlank':
                answer_type.append(str(question_type[0]))
            else:
                not_answer_type.append(str(question_type[0]))

        return answer_type, not_answer_type

    def question_accuracy(self, customerId, question_ids, cursor_3330_examlog):
        """
        学员每道试题最后的正确与否
        :param customerId:
        :param question_ids:
        :param cursor_3330_examlog:
        :return:
        """

        customer_table = f'question_record_detail_{customerId % 200}'


        question_accuracy_sql = f"SELECT q.question_id, max(q.create_date), q.is_correct from" \
            f" (SELECT question_id, create_date, is_correct from {customer_table} " \
            f"WHERE customer_id={customerId} and question_id in ({','.join(question_ids)}) ORDER BY create_date DESC) as q " \
            f"GROUP BY q.question_id"

        return self.execsql(cursor_3330_examlog, question_accuracy_sql)




if __name__ == '__main__':

    goodsId = 70557

    customerIds = [
        26079957
    ]

    start_time = '2020-08-02 00:00:00'
    end_time = '2020-08-02 23:59:59'

    q = QueryCustomerQuestionData()
    cursor_3330_examlog = q.cursor('online3330', 'examlog')
    cursor_3306_exam = q.cursor('online3306', 'exam')
    cursor_3306_highso = q.cursor('online3306', 'highso')

    for customerId in customerIds:

        print(f"学员id：{customerId}")

        # 获取商品类别和科目信息
        goods_info = q.cusormer_goods_type(goodsId, cursor_3306_highso)
        # 类别信息
        goods_category = goods_info[0][0]

        # 获取学员的商品关联的科目id
        subject_ids = []
        for info in goods_info:
            subject_ids.append(str(info[1]))

        # 获取查询时间段内，学员的商品有效期和查询时间的交集
        query_question_time = q.query_custormer_question_time(cursor_3306_highso, customerId, goodsId, start_time, end_time)

        # 按交集查询学员的做题量
        rst = q.question_sum(customerId, query_question_time[0], query_question_time[1], cursor_3330_examlog, cursor_3306_exam,
                             categoryId=goods_category, subjectIds=subject_ids)

        # 指定时间段内查询学员的做题量
        # rst = q.question_sum(customerId, query_question_time[0], query_question_time[1], cursor_3330_examlog, cursor_3306_exam,
        #                      categoryId=goods_category)

        if rst:
            print(f"主观题做题信息：{len(rst[0])}---{rst[0]}")
            print(f"客观题做题信息：{len(rst[1])}---{rst[1]}")

            question_accuracy_list = q.question_accuracy(customerId, rst[1], cursor_3330_examlog)

            right_question = []
            for qa in question_accuracy_list:
                if qa[2] == 1:
                    right_question.append(str(qa[0]))
            print(f"客观题做正确的试题信息：{len(right_question)}---{right_question}")
            print(f"客观题正确率：{len(right_question) / len(rst[1])}")
        else:
            print(f"没有做题记录")



    cursor_3330_examlog.close()
    cursor_3306_exam.close()
    cursor_3306_highso.close()




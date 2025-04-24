class ExcelDataProcessor:
    @staticmethod
    def get_class_course_mapping(df):
        """获取班级与对应课程及教师的映射关系"""
        # 过滤空值并确保唯一性
        df_filtered = df.dropna(subset=['班级名称', '课程名称', '授课教师'])
        # 按班级分组，将课程名称和教师组合成元组列表
        grouped = df_filtered.groupby('班级名称').apply(
            lambda x: list(zip(x['课程名称'], x['授课教师']))
        )
        return grouped.to_dict()

    @staticmethod
    def find_header_row(df, required_columns):
        """在 DataFrame 中查找包含所有必需列名的行"""
        for i, row in df.iterrows():
            row_values = [str(cell).strip() for cell in row]
            if required_columns.issubset(row_values):
                return i
        return None

import pandas as pd
import numpy as np
from PyQt5.QtCore import QStringListModel

class DataAnalyzer:
    def __init__(self, list_views):
        self.final_count_data_zero = []
        self.final_weather_state = []
        self.final_zero_state = []
        self.final_under_date = []
        self.final_count_data_name = []
        self.values_cnt = None
        self.list_views = list_views

    def set_values_count(self, values_cnt):
        self.values_cnt = values_cnt

    def clean_data(self, data):
        filtered_data = data[~data.apply(lambda row: row.str.contains("조회된 이력이 없습니다.").all(), axis=1)]
        return filtered_data

    def analyze_data(self, data_concat, bad_area):
        data_concat = self.clean_data(data_concat)
        if data_concat.empty:
            self.final_count_data_zero.append(bad_area)
            self.append_to_list_view(self.list_views[0], bad_area)
            return

        time_data = data_concat[['관측시간']]
        minus_time_data = time_data.iloc[:-2]
        result_nancheck = data_concat[['온도(℃)', '습도(%)', '풍속(㎧)', '풍향(degree)']]
        normal_data = data_concat[['산림 미세먼지 농도', '산업유래 휘발성유기화합물 미세먼지 농도']].iloc[:-2]
        normal_data.columns = ['col1', 'col2', 'col3', 'col4', 'col5', 'col6']
        sub1_data = normal_data[['col1', 'col2', 'col3']]
        sub2_data = normal_data[['col4', 'col5', 'col6']]
        sub2_data.columns = ['col1', 'col2', 'col3']

        try:
            result_data = sub1_data.astype(float).sub(sub2_data.astype(float))
        except Exception as e:
            print(f"오류 발생: {e}")
            return
        
        result_data.columns = ['pm10', 'pm2.5', 'pm1.0']
        time_add_result_data = pd.concat([minus_time_data, result_data], axis=1)
        condition_under = (result_data < 0).any()
        condition_zero = (normal_data == 0).any()
        check_for_nan = result_nancheck.isnull().values.any()
        filtered_data = data_concat[~data_concat.apply(lambda row: row.str.contains("조회된 이력이 없습니다.").all(), axis=1)]
        data_index_cnt = len(filtered_data.index)
        
        result_data_tail_6 = result_data.tail(6)
        final_result_data_tail_6 = (result_data_tail_6 < 0).any()
        final_plus_result_data_tail_6 = (result_data_tail_6 > 0).any()

        self.handle_counts_and_conditions(data_index_cnt, condition_zero, bad_area, normal_data, condition_under, final_result_data_tail_6, final_plus_result_data_tail_6, time_add_result_data, check_for_nan, time_data, result_nancheck)

    def handle_counts_and_conditions(self, data_index_cnt, condition_zero, bad_area, normal_data, condition_under, final_result_data_tail_6, final_plus_result_data_tail_6, time_add_result_data, check_for_nan, time_data, result_nancheck):
        if self.values_cnt is None:
            raise ValueError("values_cnt 값이 설정되지 않았습니다.")
        
        if data_index_cnt < self.values_cnt - 10:
            if data_index_cnt == 0:
                self.final_count_data_zero.append(bad_area)
            else:
                if data_index_cnt < self.values_cnt - 10:
                    time_data = time_data[~time_data.apply(lambda row: row.astype(str).str.contains('조회된 이력이 없습니다.').any(), axis=1)]
                    time_data = time_data.values
                    if len(time_data) > 1:
                        recent_time = time_data[-1]
                        if isinstance(recent_time, np.ndarray) and recent_time.size > 0:
                            datetime_str = recent_time[0]
                            self.final_count_data_name.append((bad_area, data_index_cnt, datetime_str))
                            self.append_to_list_view(self.list_views[1], f"{bad_area}, {data_index_cnt}, {datetime_str}")
        
        if condition_zero.any():
            zero_values_mask = (normal_data == 0)
            zero_counts = zero_values_mask[['col1', 'col2', 'col3', 'col4', 'col5', 'col6']].sum().sum()
            if zero_values_mask.any().any():
                self.final_zero_state.append((bad_area, zero_counts))
                self.append_to_list_view(self.list_views[2], f"{bad_area}, {zero_counts}")

        if condition_under.any():
            if final_result_data_tail_6.any() and not final_plus_result_data_tail_6.any():
                min_value_row = time_add_result_data.tail(6).loc[time_add_result_data.tail(6).idxmin().min()]
                self.final_under_date.append((bad_area, min_value_row))
                self.append_to_list_view(self.list_views[4], f"{bad_area}")
                

        if check_for_nan:
            nan_counts = result_nancheck.isnull().sum().sum()
            self.final_weather_state.append((bad_area, nan_counts))
            self.append_to_list_view(self.list_views[3], bad_area)

    def append_to_list_view(self, list_view, text):
        model = list_view.model()
        current_list = model.stringList()
        current_list.append(text)
        model.setStringList(current_list)

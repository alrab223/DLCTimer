import PySimpleGUI as sg
from datetime import datetime
import yaml
import os


class LearningTime:
   sg.theme('Material1')

   def __init__(self) -> None:
      self.calc_flag = False

   def get_log_path(self, config_path):
      with open(config_path) as file:
         config = yaml.safe_load(file)
      project_path = config_path.split("config.yaml")[0]
      iteration = config["iteration"]
      log_path = f"{project_path}dlc-models/iteration-{iteration}/"
      latest_folder = max(os.listdir(log_path), key=lambda x: os.path.getmtime(os.path.join(log_path, x)))
      log_path += f"{latest_folder}/train/log.txt"
      return log_path

   def time_calc(self, config_path, total):
      timestamp = []
      log_path = self.get_log_path(config_path)
      with open(log_path, "r")as f:
         text = f.read().splitlines()
      for i in text:
         if "iteration:" in i:
            timestamp.append(i)
      start = datetime.strptime(timestamp[0].split(" ")[0] + " " + timestamp[0].split(" ")[1], '%Y-%m-%d %H:%M:%S')
      late = datetime.strptime(timestamp[-1].split(" ")[0] + " " + timestamp[-1].split(" ")[1], '%Y-%m-%d %H:%M:%S')
      all_time = (late - start) / len(timestamp) * total
      nokori = all_time - (late - start)
      nokori = str(nokori).split(".")[0]
      return nokori

   # ログがたまるまで待機
   def log_confirmation(self, config_path):
      log_path = self.get_log_path(config_path)
      with open(log_path, "r")as f:
         text = f.read().splitlines()
      count = 0
      for i in text:
         if "iteration:" in i:
            count += 1
      return count

   def setup(self):
      self.layout = [[sg.Text("学習中のプロジェクトファイルを選択してください")],
                     [sg.Input(), sg.FileBrowse('yamlを選択', key='config_path', file_types=(("YAML", "*.yaml"),))],
                     [sg.Text('学習回数'), sg.Input(default_text="500000", size=(7, 1), enable_events=True, key='learning_total'), sg.Text('display_iterations'), sg.Input(default_text="100", size=(7, 1), enable_events=True, key='display_iterations')],
                     [sg.Button('残り時間を計算する', key='calc')],
                     [sg.Text("", font=('Noto Serif CJK JP', 10), key="_time_")],
                     [sg.Text("", font=('Noto Serif CJK JP', 30), key="_time2_")]]
      self.window = sg.Window("DLC学習時間計測", self.layout, size=(450, 200))

   def main(self):
      self.setup()
      while True:  # Event Loop
         event, values = self.window.read(timeout=3000, timeout_key='_timeout_')

         if event == sg.WIN_CLOSED:
            break

         if event == "calc":
            if values["config_path"] != "":
               self.window['_time_'].update("計測を開始します。しばらくお待ちください")
               self.calc_flag = True
            else:
               self.window['_time_'].update("ファイルが選択されていません")

         if event == "_timeout_" and self.calc_flag is True:
            if self.log_confirmation(values["config_path"]) < 3:
               self.window['_time_'].update("ログがたまるまでしばらくお待ちください")

               continue
            self.window['_time_'].update("残り学習時間を表示しています")
            nokori = self.time_calc(values["config_path"], int(values["learning_total"]) / int(values["display_iterations"]))
            self.window['_time2_'].update(nokori)
            if nokori == "0:00:00":
               self.window['_time_'].update("学習が終了しました")

      self.window.Close()


if __name__ == "__main__":
   analayze = LearningTime()
   analayze.main()

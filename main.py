import sys
import matplotlib
import matplotlib.pyplot as plt
import PySimpleGUI as sg

matplotlib.use('TkAgg')

from globals import TITLE, ABOUT, TIME_TOTAL, TIME_DELTA, TOTAL_ITEARTIONS, \
    TOTAL_WORK_PLACES_FROM, TOTAL_WORK_PLACES_TO, SPEED, DENIAL_PROBABILITY_W, DENIAL_PROBABILITY_S
from oop import RandomGenerators, Program


def main_window(rnd_gen):
    types_names = list(rnd_gen.typesNames.keys())
    layout = [
        [
            sg.Col([
                [sg.Text(TITLE, font=("Helvetica", 15))],
                [sg.Text('_' * 72)],
                [sg.Text('Введите параметры моделирования', font=("Helvetica", 14))],
                [sg.Text('Шаг изменения времени'), sg.Slider((1, 10), orientation='h', default_value=TIME_DELTA, s=(10, 15), key='time_delta')],
                [sg.Text('Время итерации (смены)'), sg.InputText(TIME_TOTAL, size=(6, 1), key='time_total')],
                [sg.Text('Тестировать число рабочих мест от'), sg.InputText(TOTAL_WORK_PLACES_FROM, size=(5, 1), key='workplaces_from'), sg.Text('до'), sg.InputText(TOTAL_WORK_PLACES_TO, size=(5, 1), key='workplaces_to')],
                [sg.Text('Общее кол-во итераций моделирования (смен)'), sg.InputText(TOTAL_ITEARTIONS, size=(5, 1), key='iterations')],
                [sg.Text('Вероятность отказа рабочих мест'), sg.InputText(DENIAL_PROBABILITY_W, size=(15, 1), key='denial_probability_w')],
                [sg.Text('Вероятность отказа накопителя'), sg.InputText(DENIAL_PROBABILITY_S, size=(15, 1), key='denial_probability_s')],
                [sg.Text('Скорость работы конвейера (м/с)'), sg.InputText(SPEED, size=(15, 1), key='speed')],
                [sg.Text('Закон распределения'), sg.Combo(types_names, size=(40, 1), default_value=types_names[0], key='type')],
                [sg.Text('_' * 72)],
                [sg.Submit('Старт')],
                [sg.Output(size=(70, 7), key='-OUTPUT-')],
                [sg.Cancel('О программе'), sg.Cancel('Выход')]
            ], element_justification='center')
        ]
    ]

    window = sg.Window(TITLE, layout, finalize=True)
    # window['-OUTPUT-'].update('')
    print("Окно сообщений программы\n")

    while True:
        event, values = window.read()

        if event == 'Старт':
            try:
                time_total = int(values['time_total'])
                time_delta = int(values['time_delta'])
                workplaces_from = int(values['workplaces_from'])
                workplaces_to = int(values['workplaces_to'])
                iterations = int(values['iterations'])
                denial_probability_w = float(values['denial_probability_w'])
                denial_probability_s = float(values['denial_probability_s'])
                speed = float(values['speed'])
            except:
                sg.popup_error('Введите верные целочисленные значения в параметрах')
                continue

            rnd_gen.setType(values['type'])
            print('Идут расчеты, не прерывайте действие программы...\n')
            window.refresh()

            me_dict, sd_dict, val_dict = Program.Main(rnd_gen, time_total, time_delta, iterations, workplaces_from,
                                            workplaces_to)
            print('Расчеты заверешены!')
            print('\nМО кол-ва изделий в зависимости от числа рабочих мест равны - ')
            print(me_dict)
            print('\nСКО кол-ва изделий в зависимости от числа рабочих мест равны - ')
            print(sd_dict)
            print('\nСреднее кол-во изделий на 1 рабочего в зависимости от числа рабочих мест равны - ')
            print(val_dict)

            plt.close()
            plt.rcParams ['figure.figsize'] = [10, 9]
            fig, axs = plt.subplots(3)
            # plt.subplots_adjust(wspace=0.5, hspace=1)
            fig.suptitle('Кол-во изделий')
            axs[0].plot(list(me_dict.keys()), list(me_dict.values()))
            axs[0].set(ylabel='МО кол-ва изделий')
            axs[1].plot(list(sd_dict.keys()), list(sd_dict.values()))
            axs[1].set(ylabel='СКО кол-ва изделий')
            axs[2].plot(list(val_dict.keys()), list(val_dict.values()))
            axs[2].set(xlabel='Число рабочих мест', ylabel='Среднее кол-во изделий на 1 рабочего')
            plt.show()

            # plt.close()
            
            # plt.plot(list(me_dict.keys()), list(me_dict.values()))
            # plt.title("МО")
            # plt.xlabel("Число рабочих мест")
            # plt.ylabel("Кол-во изделий")
            # plt.show()
            
            # plt.plot(list(me_dict.keys()), list(sd_dict.values()))
            # plt.title("СКО")
            # plt.xlabel("Число рабочих мест")
            # plt.ylabel("Кол-во изделий")
            # plt.show()

            print('-' * 50)

        if event in ('Выход', sg.WIN_CLOSED):
            window.close()
            return

        if event == 'О программе':
            sg.popup(ABOUT)


if __name__ == "__main__":
    rnd_gen = RandomGenerators()
    # rnd_gen.setType('Экспоненциальный закон распределения')
    # rnd_gen.setType('Распределенное по закону Вейбулла')
    # rnd_gen.setType('Распределенное по закону Гаусса')
    main_window(rnd_gen)
    sys.exit()
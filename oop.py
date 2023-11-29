from typing import List
import time
import sys
import random
import statistics

from globals import TIME_TOTAL, TIME_DELTA, TOTAL_PRODUCT_CREEATED, RANDOM_INIT_NUM, TOTAL_ITEARTIONS, \
    DENIAL_PROBABILITY_PL, DENIAL_PROBABILITY_S, DENIAL_PROBABILITY_W, PALLET_SIZE_X, PALLET_SIZE_Y, TOTAL_WORK_PLACES, SPEED, \
    EXPONENT_LAMBDA, GAUSS_MU, GAUSS_SIGMA, WEIBULL_ALPHA, WEIBULL_BETA, WORKER_PRODUCTIVITY


class RandomGenerators:

    typesNames = dict()
    type: str = None

    def __init__(self, randomInitNum=RANDOM_INIT_NUM):
        random.seed(randomInitNum)
        self.typesNames = {
            # 'Равномерное распределение': self.evenDistribution(),
            'Экспоненциальный закон распределения': self.exponentialDistribution,
            'Распределенное по закону Гаусса': self.gaussianDistribution,
            'Распределенное по закону Вейбулла': self.veibullDistribution
        }

    def setType(self, type):
        if type not in self.typesNames:
            print('type not in self.typesNames')
            sys.exit()
        self.type = type

    # возвращает случайное число в интервале [0; 1] распределенное по закону равномерного распределения
    def evenDistribution(self):
        return random.random()

    # возвращает случайное число распределенное по экспоненциальному закону распределения, согласно указываемому коэффициенту λ
    def exponentialDistribution(self):
        return random.expovariate(EXPONENT_LAMBDA)

    # возвращает случайное число распределенное по закону Гаусса, согласно указываемым параметрам стандартного отклонения и математического ожидания
    def gaussianDistribution(self):
        return random.gauss(GAUSS_MU, GAUSS_SIGMA)

    # возвращает случайное число распределенное по закону Вейбулла, согласно указываемым параметрам стандартного отклонения и математического ожидания
    def veibullDistribution(self):
        return random.weibullvariate(WEIBULL_ALPHA, WEIBULL_BETA)

    def selectedDistribution(self):
        if not self.type:
            print('not self.type')
            sys.exit()
        return self.typesNames[self.type]()


class Statistic():

    totalIterations: int = None #общее количество итераций статистического моделирования
    ValuesTitles: list = None #массив для сохранения названий значений переменных, для которых собираются статистические данные
    Values: dict = None #массив для сохранения текущих значений переменных, для которых собираются статистические данные
    MathExpectations: dict = None #массив для хранения результатов вычисления математического ожидания каждой из переменных, для которых собираются статистические данные
    StandartDeviations: dict = None #массив для хранения результатов вычисления стандартного отклонения каждой из переменных, для которых собираются статистические данные

    # конструктор класса, инициирующий все необходимые переменные и массивы, которому передается один единственный параметр totalIterationsIn – общее кол-во итераций статистического моделирования
    def __init__(self, totalIterationsIn=TOTAL_ITEARTIONS):
        self.totalIterations = totalIterationsIn
        self.ValuesTitles = ['products']
        self.Values = {key: dict() for key in self.ValuesTitles}
        self.MathExpectations = dict()
        self.StandartDeviations = dict()

    # метод, используемый для записи i-го текущего значения переменной
    # передаются следующие параметры: position – номер итерации статистического моделирования; value – значение переменной в данной итерации статистического моделирования; valueTitle – название переменной.
    def RecordValue(self, position, value, valueTitle):
        if valueTitle not in self.ValuesTitles:
            self.ValuesTitles.append(valueTitle)
            self.Values[valueTitle] = dict()
        self.Values[valueTitle][position] = value

    # метод для расчета математического ожидания для всех переменных
    def CalculateMathExpectation(self, valueTitle):
        return statistics.mean(list(self.Values[valueTitle].values()))

    # метод для расчета стандартного отклонения для всех переменных
    def CalculateStandartDeviation(self,valueTitle):
        return statistics.stdev(list(self.Values[valueTitle].values()))

    # метод для очистки массива текущих значений переменных
    def ClearValue(self, valueTitle):
        self.Values[valueTitle] = dict()

    # метод для отображения рассчитаных значений МО и СКО для всех переменных
    def DisplayInfo(self):
        print(self.Values)


class Store:

    assemblyDepartmentIn = None
    denialProbabilityIn: float = None
    total_time = None

    # конструктор класса накопителя
    def __init__(self, assemblyObject, denialProbability=DENIAL_PROBABILITY_S):
        self.assemblyDepartmentIn = assemblyObject
        self.denialProbabilityIn = denialProbability
        self.total_time = 0

    # переопределяет способ генерации времени устранения организационно-технического отказа (ремонта) для накопителя
    def GenerateNewRepairTime(self):
        self.total_time += self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # осуществляет прием сборочного комплекта с конвейера
    def ReceiveFromProductionLine(self):
        self.total_time += self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # осуществляет загрузку собранного изделия на конвейер
    def SendToProductionLine(self):
        self.total_time += self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # осуществляет выполнение одного шага моделирования для накопителя и в случае успешного выполнения возвращает 0
    def RunIteration(self, cur_time):
        self.GenerateNewRepairTime()
        self.ReceiveFromProductionLine()
        self.SendToProductionLine()


class ProductionLine:

    totalWorkPlacesIn: int = None
    assemblyDepartmentIn = None
    denialProbabilityIn: float = None

    workPlace: list = None #массив рабочих мест, обслуживаемых конвейером
    mode: bool = None #определяет текущий режим работы конвейера: 0 – режим загрузки рабочих мест; 1 – режим выгрузки рабочих мест
    modeWorkTimeLeft: float = None #определяет остаток времени работы в текущем режиме в секундах
    modeWorkTimeDependentLeft: float = None #определяет остаток времени работы, зависящий от работоспособности накопителя в текущем режиме в секундах
    modeWorkPlaceWaiting: list = None #является массивом рабочих мест, ожидающих действий от конвейера в его текущем режиме
    speed: float = None #определяет скорость конвейера в метрах в секунду (Vx = Vy)
    palletSizeX: float = None #определяет размер паллеты по горизонтали в метрах
    palletSizeY: float = None #определяет размер паллеты по вертикали в метрах

    totalProducts = None
    workerProductivity = None

    # конструктор класса конвейера
    def __init__(self, assemblyDepartmentIn, speedIn=SPEED, palletSizeXIn=PALLET_SIZE_X, palletSizeYIn=PALLET_SIZE_Y,
                 denialProbabilityIn=DENIAL_PROBABILITY_PL, workerProductivity=WORKER_PRODUCTIVITY):
        self.assemblyDepartmentIn = assemblyDepartmentIn
        self.denialProbabilityIn = denialProbabilityIn

        self.speed = speedIn
        self.totalWorkPlacesIn = assemblyDepartmentIn.totalWorkPlaces
        self.palletSizeX = palletSizeXIn
        self.palletSizeY = palletSizeYIn
        self.workerProductivity = workerProductivity

        self.totalProducts = 0

    # рассчитывает и возвращает время необходимое для выполнения всех запросов в текущем режиме в секундах
    def calculateModeWorkTime(self):
        self.modeWorkTimeLeft = self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # функция переопределения способа генерации времени и устранения организационно-технического отказа (ремонта) для конвейера в секундах
    def GenerateNewRepairTime(self):
        self.modeWorkPlaceWaiting = self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # выполняет один шаг моделирования для конвейера, в случае успешного выполнения возвращает 0
    def RunIteration(self, cur_time):
        self.calculateModeWorkTime()
        self.GenerateNewRepairTime()
        self.totalProducts += self.speed * self.totalWorkPlacesIn * self.workerProductivity


class WorkPlace:

    finalStoreSize: int = None #емкость выходного накопителя (максимальное кол-во доступных мест)
    initialStoreSize: int = None #емкость входного накопителя
    productionLineIndex: int = None #номер рабочего места на конвейере
    currentFinalStoreSize: int = None #текущая загрузка выходного накопителя (текущее количество занятых мест)
    currentInitialStoreSize: int = None #текущая загрузка входного накопителя (текущее кол-во занятых мест)
    currentOperationTime: float = None #время выполнения текущей операции в секундах
    finalStore = None #выходной накопитель
    indexInProductionLine: int = None #номер рабочего места на конвейере
    initialStore = None #входной накопитель
    maxFinalStoreSize: int = None #емкость выходного накопителя (максимальное кол-во доступных мест)
    maxInitialStoreSize: int = None #емкость входного накопителя (максимальное кол-во доступных мест)
    assemblyDepartmentIn = None
    total_time = None

    # конструктор класса рабочего места
    def __init(self, assemblyDepartmentIn, indexInProductionLineIn, maxInitialStoreSizeIn, maxFinalStoreSizeIn, denialProbabilityIn=DENIAL_PROBABILITY_W):
        self.assemblyDepartmentIn = assemblyDepartmentIn
        self.denialProbabilityIn = denialProbabilityIn
        self.indexInProductionLine = indexInProductionLineIn
        self.maxInitialStoreSize = indexInProductionLineIn
        self.maxFinalStoreSize = indexInProductionLineIn
        self.total_time = 0

    # процедура переопределения способа генерации времени и  устранения организационно-технического отказа (ремонта) для рабочего места в секундах
    def GenerateNewRepairTime(self):
        self.total_time += self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # процедура, опрашивающая, есть ли во входном накопителе свободное место, возвращает истина (true), если да и ложь (false), если нет
    def HasFreePlaceInInitialStore(self):
        return self.assemblyDepartmentIn.random_generator.eventDistribution()

    # процедура получения продукта с конвейера во входной накопитель, возвращает истина (true) если процедура прошла успешно и ложь (false) если нет
    def ReceiveProduct(self):
        self.total_time += self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # процедура сдачи продукта на конвейер с выходного накопителя, возвращает индекс партии деталей, к которой принадлежит текущая деталь
    def SendProduct(self):
        self.total_time += self.assemblyDepartmentIn.random_generator.selectedDistribution()

    # выполнение одного шага моделирования для рабочего места, в случае успешного выполнения возвращает 0
    def RunIteration(self, cur_time):
        if round(self.HasFreePlaceInInitialStore()):
            self.ReceiveProduct()
        self.SendProduct()


class ProductionSet:

    size: int = None #размер партии, штук деталей
    recievedFromFinalStore: int = None #количество деталей из этой партии полученных с выходного накопителя
    sendedToInitialStore: int = None #количество деталей из этой партии отправленных на входной накопитель

    # конструктор класса партии деталей
    def __init(self, store):
        self.store = store
        self.recievedFromFinalStore = 0
        self.sendedToInitialStore = 0

    # имитирует отгрузку деталей с выходного накопителя
    def ReceiveFromFinalStore(self):
        self.recievedFromFinalStore += self.store

    # имитирует отгрузку деталей на входной накопитель
    def SendToInitialStore(self):
        self.recievedFromFinalStore -= self.store


class AssemblyDepartment:

    timeTotal: int = None #общее время моделирования в секундах (время смены = 480 * 60)
    timeDelta: int = None #шаг изменения времени в секундах (1 сек)
    timeCurrent: int = None #текущее время в секундах
    initialStore: Store = None #экземпляры класса Store, который является моделью входного и выходного накопителей
    finalStore: Store = None #экземпляры класса Store, который является моделью входного и выходного накопителей
    productionLine: ProductionLine = None #является экземпляром класса ProductionLine, описывающего работу конвейера
    productionSetArray: List[ProductionSet] = None #является экземпляром системного класса ArrayList, описвающий массив партий деталей (объекты типа ProductionSet)
    totalProductsCreated: int = None #общее количество изделий принятых на текущий момент из выходного накопителя
    statistic: Statistic = None
    commonDenial = None
    random_generator: RandomGenerators = None
    totalIterations: int = None
    totalWorkPlaces: int = None
    total_products = None

    # конструктор класса сборочного цеха
    def __init__(self, rnd_gen, timeTotal=TIME_TOTAL, timeDelta=TIME_DELTA, totalIterationsIn=TOTAL_ITEARTIONS, totalWorkPlaces=TOTAL_WORK_PLACES, totalProductsCreated=TOTAL_PRODUCT_CREEATED):
        self.timeTotal = timeTotal
        self.timeDelta = timeDelta
        self.timeCurrent = 0
        self.initialStore = Store(self)
        self.finalStore = Store(self)
        self.totalIterations = totalIterationsIn
        self.totalWorkPlaces = totalWorkPlaces

        self.statistic = Statistic()
        self.random_generator = rnd_gen
        self.commonDenial = CommonDenial(self)

        self.productionSetArray = []
        self.generateNewProductionSet()

        self.totalProductsCreated = totalProductsCreated
        self.total_products = 0

    # позволяет отобразить информацию о текущем состоянии сборочного цеха
    def DisplayCurrentInfo(self):
        print('timeCurrent:', self.timeCurrent)
        print('totalProductsCreated:', self.totalProductsCreated)

    # генерирует новую партию деталей и добавляет ее в динамический массив productionSetArray
    def generateNewProductionSet(self):
        new_prodiction_set = ProductionSet()
        self.productionSetArray.append(new_prodiction_set)

    # осуществяет выполение одного шага моделирования для сборочного цеха (например, моделируется одна смена)
    def RunIteration(self):
        for iteration in range(self.totalIterations):
            self.productionLine = ProductionLine(self)
            self.commonDenial.currentState = True
            self.total_products = 0
            for i in range(0, self.timeTotal, self.timeDelta):
                self.timeCurrent = i

                self.commonDenial.RunIteration(i)
                if self.commonDenial.currentState:
                    self.productionLine.RunIteration(i)

                self.generateNewProductionSet()

            self.total_products = self.productionLine.totalProducts * (1 - self.random_generator.selectedDistribution() * self.commonDenial.denialProbability * self.totalWorkPlaces * 10)
            # self.total_products = self.productionLine.totalProducts * (
            #             1 - self.random_generator.selectedDistribution() * self.commonDenial.denialProbability * self.totalWorkPlaces - self.commonDenial.denialProbability * self.totalWorkPlaces * (self.totalWorkPlaces ** 0.8))

            self.totalProductsCreated += self.total_products

            # print(self.total_products / self.totalWorkPlaces)
            self.statistic.RecordValue(iteration, self.total_products, 'products')
            # print(self.total_products)
        me = round(self.statistic.CalculateMathExpectation('products'))
        sd = round(self.statistic.CalculateStandartDeviation('products'), 2)
        return (me, sd)


class CommonDenial(ProductionLine, Store, WorkPlace):

    assemblyDepartment: AssemblyDepartment = None #является ссылкой на родительский экземпляр класса AssemblyDepartment
    denialProbability: float = None #вероятность отказа [0; 1] за время указанное в переменной assemblyDepartment.timeDelta
    timeDenial: float = None #общее время простоя объекта из-за организационно-технического отказа в секундах
    timeEffectiveWork: float = None #эффективное время работы объекта в секундах
    timeRepair: float = None #время устранения организационно-технического отказа (ремонт) объекта в секундах
    timeWork: float = None #общее время работы объекта в секундах
    currentState: bool = None #состояние объекта: 0 – работает нормально; 1 – организационно-технический отказ
    random_generator: RandomGenerators = None
    repair_time: float = None
    stop_time = None

    # конструктор класса общего отказа
    def __init__(self, assemblyDepartmentIn):
        super().__init__(assemblyDepartmentIn)
        self.assemblyDepartment = assemblyDepartmentIn
        if (DENIAL_PROBABILITY_PL != 0) or (DENIAL_PROBABILITY_W != 0) or (DENIAL_PROBABILITY_S != 0): 
            self.denialProbability = max(DENIAL_PROBABILITY_PL, DENIAL_PROBABILITY_W, DENIAL_PROBABILITY_S)
        self.random_generator = assemblyDepartmentIn.random_generator
        self.currentState = True
        self.repair_time = 0
        self.stop_time = 0

    # определяет способ генерации времени устранения организационно-технического отказа (ремонта) для объекта в секундах
    def GenerateNewRepairTime(self):
        self.repair_time = self.random_generator.selectedDistribution()

    # осуществляет выполение одного шага моделирования для объекта общего отказа
    def RunIteration(self, cur_time):
        if self.currentState:
            if self.denialProbability >= self.random_generator.evenDistribution():
                self.currentState = False
                self.GenerateNewRepairTime()
                self.stop_time = cur_time
        else:
            if cur_time >= self.stop_time + self.repair_time:
                self.currentState = True
                self.repair_time = 0
                self.stop_time = 0


class Program():
    @staticmethod
    def Main(rnd_gen, timeTotal, timeDelta, totalIterationsIn, totalWorkPlacesFrom, totalWorkPlacesTo):
        me_dict = dict()
        sd_dict = dict()
        val_dict = dict()
        for totalWorkPlaces in range(totalWorkPlacesFrom, totalWorkPlacesTo + 1):
            assembly = AssemblyDepartment(rnd_gen, timeTotal, timeDelta, totalIterationsIn, totalWorkPlaces)
            me, sd = assembly.RunIteration()
            me_dict[totalWorkPlaces] = me
            sd_dict[totalWorkPlaces] = sd
            val_dict[totalWorkPlaces] = round(me / totalWorkPlaces, 2)
        return me_dict, sd_dict, val_dict
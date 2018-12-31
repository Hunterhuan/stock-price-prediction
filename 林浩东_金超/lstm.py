#begin LSTM
import numpy
import csv
import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Activation, Dropout
from keras.utils import np_utils
from keras import regularizers
from keras.callbacks import EarlyStopping
import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def normalization0(train_data):
    #�����ݽ������򻯴���(-1,1)
    m = numpy.mean(train_data)
    tmin,tmax = train_data.min(),train_data.max()
    return (train_data - m)/(tmax-tmin)

def normalization1(train_data):
        #�����ݽ������򻯴���(0,1)
        tmin,tmax = train_data.min(),train_data.max()
        return(train_data - tmin)/(tmax - tmin)

def pre_deal(train_data):
    """"Ԥ�����л�����������ϴ"""
    #��ѵ�����ݽ���Ԥ����
    #������ת��Ϊ����
    for i in range(len(train_data)-1,0,-1):
       train_data[i] = train_data[i] - train_data[i-1]
    train_data[0] = train_data[0] - train_data[0]
    normalization0(train_data)
    return train_data

def get_data(path):
    #��ȡѵ������
    data = numpy.loadtxt(path,delimiter= ',' ,skiprows=1,usecols=(3,4,6,7,8,9))
    return data

def create_model_data(train_data):
    #ѵ������׼��
    dataX = train_data[:,1:]
    dataY = train_data[:,0:1]
    dataX = pre_deal(dataX)
    datasetX = dataX[:int(len(dataX)/10)*10-20,:]
    datasetY = []
    for i in range(int(len(dataX)/10)-2):
        temp = 0
        for j in range(20):
            temp = temp + dataY[10*(i+1)+j] - dataY[10*(i+1)-1]
        datasetY.append(temp/20)
    datasetX = datasetX.reshape(int(len(datasetX)/10),50,1)
    datasetX = numpy.array(datasetX)
    datasetY = numpy.array(datasetY) 
    numpy.save("trainX.npy",datasetX)
    numpy.save("trainY.npy",datasetY)

def create_pred_data(test_data):
    dataX = test_data[:,1:]
    dataY = test_data[:,0:1]
    dataX = pre_deal(dataX)
    datasetX = dataX[:,:]
    datasetX = datasetX.reshape(int(len(datasetX)/10),50,1)
    datasetY = []
    for i in range(int(len(datasetX))):
        datasetY.append(dataY[10*(i+1)-1])
    datasetX = numpy.array(datasetX)
    datasetY = numpy.array(datasetY)
    numpy.save("testX.npy",datasetX)
    numpy.save("testY.npy",datasetY)
    return datasetX,datasetY

def predict(model):
    test_data = get_data("test_data.csv")
    testX,testY = create_pred_data(test_data)
    result = model.predict(testX)
    result = result + testY
    return result


def output_result(result,road):
    #resultΪԤ��õ��Ľ��
    stu = ['caseid','midprice']
    out = open(road,'w', newline='')
    csv_write = csv.writer(out,dialect='excel')
    csv_write.writerow(stu)
    for i in range(142,1000):
        temp = [i+1,result[i][0]]
        csv_write.writerow(temp)

def get_model(lstmFirstLayer,lstmSecondLayer,lstmThirdLayer,lo,opt):
    trainX = numpy.load("trainX.npy")
    trainY = numpy.load("trainY.npy")
    testX = numpy.load("testX.npy")
    testY = numpy.load("testY.npy")
    print("have dealed")
    #����������
    model = Sequential()
    model.add(LSTM(lstmFirstLayer, input_shape=(trainX.shape[1], trainX.shape[2]),return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(lstmSecondLayer,return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(lstmThirdLayer,return_sequences=False))
    model.add(Dropout(0.3))
    '''model.add(Dense(60,activation="tanh", kernel_regularizer=regularizers.l2(0.001)))
    model.add(Dropout(0.2))'''
    model.add(Dense(units=1,activation='tanh'))
    #rmsprop = keras.optimizers.RMSprop(lr=0.0001)
    #model.compile(loss="mse", optimizer=rmsprop)
    #model.compile(loss="mse", optimizer="adagrad")
    model.compile(loss=lo, optimizer=opt)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5)
    model.fit(trainX,trainY,batch_size=100,epochs=100,validation_split=0.25,verbose=1,shuffle=False,callbacks=[early_stopping])
    #���в���
    #testScore = model.evaluate(testX, testY,batch_size=365, verbose=1)
    #print("Model Accuracy: %.2f%%" % (testScore*100))
    #����model
    """hyperparams_name=str(lstmFirstLayer)+"-"+str(lstmSecondLayer)
    model.save(os.path.join('MODEL{}_cont.h5'.format(hyperparams_name)))"""
    return model

def create_total_data():
    create_model_data(get_data("train_data.csv"))
    create_pred_data(get_data("test_data.csv"))

def main():
    create_total_data()
    lstmFirstLayer,lstmSecondLayer,lstmThirdLayer = 30,30,30
    loss,opt = "mae","rmsprop"
    hyperparams_name=str(lstmFirstLayer)+"-"+str(lstmSecondLayer)+"-"+loss + "-" + opt
    road = os.path.join('MODEL{}_cont.h5'.format(hyperparams_name))
    train_data = get_data("train_data.csv")
    model = get_model(lstmFirstLayer,lstmSecondLayer,lstmThirdLayer,loss,opt)
    result = predict(model)
    r = os.path.join('RESULT{}_cont.csv'.format(hyperparams_name))
    output_result(result,r)
main()

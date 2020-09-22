import sys
sys.path.insert(0,'/Users/jongm/SBAprojects')
from titanic.service import Service
from titanic.entity import Entity

class Controller:
    def __init__(self):
        self.service = Service()
        self.entity = Entity()

    def preprocessing(self,train,test):
        service = self.service
        this = self.entity
        this.train = service.new_model(train)  #payload
        this.test = service.new_model(test)  #payload
        return this

    def modeling(self,train,test):
        service = self.service
        this = self.preprocessing(train,test)
        print(f'훈련 컬럼 : {this.train.columns}')
        this.label = service.create_label(this)
        this.train = service.create_train(this)
        return this


    def learning(self):
        pass

    def submit(self):
        pass

if __name__ =='__main__':
    ctrl = Controller()
    ctrl.modeling('train.csv','test.csv')
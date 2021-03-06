
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
basedir = os.path.dirname(os.path.abspath(__file__))
from util.file_handler import FileReader
# from config import basedir
import pandas as pd
import numpy as np 
from config import basedir
# sklearn algo: classification, regression, clustering, dim-reduction, 
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold   # k 값은 count의 의미
from sklearn.model_selection import cross_val_score
# dtree,rforest,nb,knn,svm
"""
context path : /Users/jongm/SBAprojects
fname : /kaggle/data/

PassengerId  고객ID, @@@문제
Survived 생존여부,  @@@답

Pclass 승선권 1 = 1등석, 2 = 2등석, 3 = 3등석,
Name,
Sex,
Age,
SibSp 동반한 형제, 자매, 배우자,
Parch 동반한 부모, 자식,
Fare 요금,
Embarked 승선한 항구명 C = 쉐브루, Q = 퀸즈타운, S = 사우스햄튼

###########Ticket 티켓번호,
###########Cabin 객실번호,
"""

class Service:
    def __init__(self):
        self.fileReader = FileReader()
        self.kaggle = os.path.join(basedir, 'kaggle')
        self.data = os.path.join(self.kaggle, 'data')

    def new_model(self,payload):
        this = self.fileReader
        this.data = self.data 
        this.fname = payload
        return pd.read_csv(os.path.join(self.data, this.fname))   # 교과서 p.139  df = tensor

    @staticmethod 
    def create_train(this) -> object :
        return this.train.drop('Survived', axis = 1)  # train은 답이 제거된 데이터셋

    @staticmethod
    def create_label(this) -> object :  #categorical
        return this.train['Survived'] 
        ######### label - 답        feature=variables

    @staticmethod
    def drop_feature(this,feature) -> object:
        this.train = this.train.drop([feature], axis = 1)
        this.test = this.test.drop([feature], axis= 1) #p.149보면 train,test로 split
        return this

    @staticmethod
    def pclass_ordinal(this) ->object:
        return this
        
    @staticmethod
    def name_nominal(this)->object:
        return this

    @staticmethod
    def title_nominal(this) ->object:
        combine = [this.train, this.test]
        for dataset in combine : 
            dataset['Title'] = dataset['Name'].str.extract('([A-Za-z]+)\.', expand=False)
        for dataset in combine:
            dataset['Title'] = dataset['Title'].replace(['Capt','Col','Don','Dr','Major','Rev','Jonkheer','Dona','Mme'], 'Rare')
            dataset['Title'] = dataset['Title'].replace(['Countess','Lady','Sir'], 'Royal')
            dataset['Title'] = dataset['Title'].replace('Ms','Miss')
            dataset['Title'] = dataset['Title'].replace('Mlle','Mr')
        title_mapping = {
            'Mr':1,
            'Miss':2,
            'Mrs':3,
            'Master':4,
            'Royal':5,
            'Rare':6
            }
        for dataset in combine: 
            dataset['Title'] = dataset['Title'].map(title_mapping)
            dataset['Title'] = dataset['Title'].fillna(0) #Unknown
        this.train = this.train
        this.test = this.test
        
        return this

    @staticmethod
    def sex_nominal(this) ->object:
        combine = [this.train, this.test]
        sex_mapping = {'male':0, 'female':1}
        for dataset in combine:
            dataset['Sex'] = dataset['Sex'].map(sex_mapping)

        this.train = this.train #overriding
        this.test = this.test 
        return this
    
    @staticmethod
    def age_ordinal(this) -> object:
        train = this.train
        test = this.test 
        train['Age'] = train['Age'].fillna(-0.5)
        test['Age'] = test['Age'].fillna(-0.5)
         # age 를 평균으로 넣기도 애매하고, 다수결로 넣기도 너무 근거가 없다...
         # 특히 age 는 생존률 판단에서 가중치(weigth)가 상당하므로 디테일한 접근이 필요합니다.
         # 나이를 모르는 승객은 모르는 상태로 처리해야 값의 왜곡을 줄일수 있어서 
         # -0.5 라는 중간값으로 처리했습니다.
        bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf] # 이 파트는 범위를 뜻합니다.
         # -1 이상 0 미만....60이상 기타 ...
         # [] 에 있으니 이것은 변수명이겠군요..라고 판단하셨으면 잘 이해한 겁니다.
        labels = ['Unknown', 'Baby', 'Child', 'Teenager','Student','Young Adult', 'Adult', 'Senior']
        # [] 은 변수명으로 선언되었음
        train['AgeGroup'] = pd.cut(train['Age'], bins, labels=labels)
        test['AgeGroup'] = pd.cut(train['Age'], bins, labels=labels)
        age_title_mapping = {
            0: 'Unknown',
            1: 'Baby',
            2: 'Child',
            3: 'Teenager',
            4: 'Student',
            5: 'Young Adult',
            6: 'Adult',
            7: 'Senior'
        } # 이렇게 []에서 {} 으로 처리하면 labels 를 값으로 처리하겠네요.
        for x in range(len(train['AgeGroup'])):
            if train['AgeGroup'][x] == 'Unknown':
                train['AgeGroup'][x] = age_title_mapping[train['Title'][x]]
        for x in range(len(test['AgeGroup'])):
            if test['AgeGroup'][x] == 'Unknown':
                test['AgeGroup'][x] = age_title_mapping[test['Title'][x]]
        
        age_mapping = {
            'Unknown': 0,
            'Baby': 1,
            'Child': 2,
            'Teenager': 3,
            'Student': 4,
            'Young Adult': 5,
            'Adult': 6,
            'Senior': 7
        }
        train['AgeGroup'] = train['AgeGroup'].map(age_mapping)
        test['AgeGroup'] = test['AgeGroup'].map(age_mapping)
        this.train = train
        this.test = test
        return this
    
    @staticmethod
    def sibsp_numeric(this)->object:
        return this

    @staticmethod
    def parch_numeric(this)->object:
        return this
    
    @staticmethod
    def fare_ordinal(this) -> object:
        this.train['FareBand'] = pd.qcut(this['Fare'], 4, labels={1,2,3,4})
        this.test['FareBand'] = pd.qcut(this['Fare'], 4, labels={1,2,3,4})
        return this


    @staticmethod
    def fareBand_nominal(this)->object:  #요금이 다양하니 클러스터링을 하기위한 준비
        this.train = this.train.fillna({'FareBand' : 1})  # FareBand라는 변수추가
        this.test = this.test.fillna({'FareBand' : 1})
        return this

    @staticmethod
    def embarked_nominal(this)->object:
        this.train = this.train.fillna({'Embarked': 'S'})
        this.test = this.test.fillna({'Embarked':'S'})
        # ml library assumes class label in Z
        # 교과서 146 문자 blue=0 green=1 red=2 로 치환
        this.train['Embarked'] = this.train['Embarked'].map({'S':1,'C':2,'Q':3})
        this.test['Embarked'] = this.test['Embarked'].map({'S':1,'C':2,'Q':3})
        # ordinal 아님
        return this

    # MachineLearning 중 dtree,rforest,nb,knn,svm 사용

    @staticmethod
    def create_k_fold():
        return KFold(n_splits = 10, shuffle = True, random_state=0)

    def accuracy_by_dtree(self,this):
        dtree = DecisionTreeClassifier()
        score = cross_val_score(dtree, this.train, this.label, cv = Service.create_k_fold(), n_jobs=1, scoring='accuracy')
        return round(np.mean(score)*100,2)
        
    def accuracy_by_rforest(self,this):
        rforest = RandomForestClassifier()
        score = cross_val_score(rforest, this.train, this.label, cv = Service.create_k_fold(), n_jobs=1, scoring='accuracy')
        return round(np.mean(score)*100,2)
        
    def accuracy_by_nb(self,this):
        nb = GaussianNB()
        score = cross_val_score(nb, this.train, this.label, cv = Service.create_k_fold(), n_jobs=1, scoring='accuracy')
        return round(np.mean(score)*100,2)
        
    def accuracy_by_knn(self,this):
        knn = KNeighborsClassifier()
        score = cross_val_score(knn, this.train, this.label, cv = Service.create_k_fold(), n_jobs=1, scoring='accuracy')
        return round(np.mean(score)*100,2)
        
    def accuracy_by_svm(self,this):
        svm = SVC()
        score = cross_val_score(svm, this.train, this.label, cv = Service.create_k_fold(), n_jobs=1, scoring='accuracy')
        return round(np.mean(score)*100,2)



class Controller:
    def __init__(self):
        self.fileReader = FileReader()
        self.kaggle = os.path.join(basedir, 'kaggle')
        self.data = os.path.join(self.kaggle, 'data')
        self.service = Service()

    def modeling(self,train,test):
        service = self.service
        this = self.preprocessing(train,test)
        print(f'훈련 컬럼 : {this.train.columns}')
        this.label = service.create_label(this)
        this.train = service.create_train(this)
        return this

    def preprocessing(self,train,test):
        service = self.service
        this = self.fileReader
        this.train = service.new_model(train)  #payload
        this.test = service.new_model(test)  #payload
        this.id = this.test['PassengerId'] #machine에게 question이됌
        print(f'드롭 전 변수: {this.train.columns}')
        this = service.drop_feature(this, 'Cabin')
        this = service.drop_feature(this, 'Ticket')
        print(f'드롭 후 변수: {this.train.columns}')


        this = service.embarked_nominal(this)
        print(f'승선한 항구 정제결과:\n{this.train.head()}')
        this = service.title_nominal(this)
        print(f'타이틀 정제결과:\n{this.train.head()}')
        # name변수에서 title을 추출했으니 name은 필요가 없어짐
        # str이니, 후에 ML-lib 가 이를 인식하는 과정에서 에러낼꺼임
        # 삭제해야댐
        this = service.drop_feature(this, 'Name')
        this = service.drop_feature(this, 'PassengerId')
        this = service.age_ordinal(this)
        print(f'나이 정제결과: \n {this.train.head()}')
        this = service.sex_nominal(this)
        print(f'성별 정제결과: \n {this.train.head()}')
        this = service.fareBand_nominal(this)
        print(f'요금 정제결과: \n {this.train.head()}')
        this = service.drop_feature(this, 'Fare')
        print(f'전체 정제결과: \n {this.train.head()}')
        print(f'train na 체크: \n {this.train.isnull().sum()}')
        print(f'test na 체크: \n {this.test.isnull().sum()}')

        return this

    def learning(self,train,test):
        service = self.service
        this = self.modeling(train,test)
        print('=====================  Learning 결과 ===================')
        print(f'결정트리 검증결과: {service.accuracy_by_dtree(this)}')
        print(f'램덤포레스트 검증결과: {service.accuracy_by_rforest(this)}')
        print(f'나이브베이즈 검증결과: {service.accuracy_by_nb(this)}')
        print(f'knn 검증결과: {service.accuracy_by_knn(this)}')
        print(f'svm 검증결과: {service.accuracy_by_svm(this)}')
        ##########여기까지 모델링

    def submit(self, train, test): #machine이 된다. 캐글에게 내 머신을 보내서 평가받는것
        this = self.modeling(train,test)
        clf = RandomForestClassifier()
        clf.fit(this.train, this.label)
        prediction = clf.predict(this.test)
        pd.DataFrame(
            {'PassengerId' : this.id, 'Survived' : prediction}
        ).to_csv( os.path.join(self.data, 'submission.csv'), index=False)


if __name__ =='__main__':
    print(f'*********************{basedir}*************')
    ctrl = Controller()
    ctrl.submit('train.csv','test.csv')
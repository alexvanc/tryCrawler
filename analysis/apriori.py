import itertools

class Apriori:
    def __init__(self,min_sup=0.2,dataDic={}):
        self.data = dataDic
        self.size = len(dataDic) #Get the number of events
        self.min_sup = min_sup
        self.min_sup_val = min_sup * self.size

    def find_frequent_1_itemsets(self):
        FreqDic = {} #{itemset1:freq1,itemsets2:freq2}
        for event in self.data:
            for item in self.data[event]:
                if item in FreqDic:
                    FreqDic[item] += 1
                else:
                    FreqDic[item] = 1
        L1 = []
        for itemset in FreqDic:
            if itemset >= self.min_sup_val:
                L1.append([itemset])
        return L1

    def has_infrequent_subset(self,c,L_last,k):
        subsets = list(itertools.combinations(c,k-1)) #return list of tuples of items
        for each in subsets:
            each = list(each) #change tuple into list
            if each not in L_last:
                return True
        return False
            
    def apriori_gen(self,L_last): #L_last means frequent(k-1) itemsets
        k = len(L_last[0]) + 1
        Ck = []
        for itemset1 in L_last:
            for itemset2 in L_last:
                #join step
                flag = 0
                for i in range(k-2):
                    if itemset1[i] != itemset2[i]:
                        flag = 1 #the two itemset can't join
                        break;
                if flag == 1:continue
                if itemset1[k-2] < itemset2[k-2]:
                    c = itemset1 + [itemset2[k-2]]
                else:
                    continue

                #pruning setp
                if self.has_infrequent_subset(c,L_last,k):
                    continue
                else:
                    Ck.append(c)
        return Ck

    def do(self):
        L_last = self.find_frequent_1_itemsets()
        L = L_last
        i = 0
        while L_last != []:
            Ck = self.apriori_gen(L_last)
            FreqDic = {}
            for event in self.data:
                #get all suported subsets
                for c in Ck:
                    if set(c) <= set(self.data[event]):#is subset
                        if tuple(c) in FreqDic:
                            FreqDic[tuple(c)]+=1
                        else:
                            FreqDic[tuple(c)]=1
            # print FreqDic
            Lk = []
            for c in FreqDic:
                if FreqDic[c] > self.min_sup_val:
                    Lk.append(list(c))
            L_last = Lk
            L += Lk
        return L

#******Test******
# Data = {'T100':['I1','I2','I5'],
#         'T200':['I2','I4'],
#         'T300':['I2','I3'],
#         'T400':['I1','I2','I4'],
#         'T500':['I1','I3'],
#         'T600':['I2','I3'],
#         'T700':['I1','I3'],
#         'T800':['I1','I2','I3','I5'],
#         'T900':['I1','I2','I3']}

# a=Apriori(dataDic=Data)
# print a.do()
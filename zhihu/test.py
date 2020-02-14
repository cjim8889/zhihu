import json
import operator
import pkuseg

if __name__ == "__main__":

    dic = dict()

    seg = pkuseg.pkuseg(postag=True)       
    # seg = pkuseg.pkuseg()       


    with open('answers-358967893-12-2-19-42.json', 'r', encoding='utf-8') as f:
        answers = json.load(f)

        for a in answers:
            words = seg.cut(a['content'])

            for w in words:
                if w[1] == 'w' or w[1] == 'x' or w[1] == 'u' or w[1] == 'r' or w[1] == 'y' or w[1] == 'e' or w[1] == 'o':
                    continue


                if w[0] not in dic:
                    dic[w[0]] = 1
                else:
                    dic[w[0]] += 1
        
        sorted_x = sorted(dic.items(), key=operator.itemgetter(1))


        print(sorted_x)
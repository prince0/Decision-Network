# @author Prince Chopra
from decimal import Decimal
import copy
import itertools


def topological_sort(network_dictionary):
    var = network_dictionary.keys()
    var = sorted(var)
    temp = []
    while len(temp) < len(var):
        for v in var:
            if v not in temp and all(x in temp for x in network_dictionary[v]['Parents']):
                temp.append(v)
    return temp


baysian_network = {}
query_list = []
input_file = open('test/input2.txt', 'r')
next_line = input_file.readline()
next_line = ''.join(c for c in next_line if c not in '\n')
while next_line != '******':
    query_list.append(next_line)
    next_line = input_file.readline()
    next_line = ''.join(c for c in next_line if c not in '\n')

first = input_file.readline()
first = ''.join(c for c in first if c not in '\n')

while first != '':
    next = first
    if '|' not in next:
        decision = input_file.readline()
        decision = ''.join(c for c in decision if c not in '\n')
        if decision[0] == 'd':
            baysian_network[next.strip('\n')] = {'Parents': [], 'Probability': decision.strip('\n'),
                                                 'cpt': [], 'Type': 'Decision'}
            baysian_network[next.strip('\n')]['Children'] = []
        else:
            baysian_network[next.strip('\n')] = {'Parents': [], 'Probability': decision.strip('\n'),
                                                 'cpt': [], 'Type': 'Normal'}
            baysian_network[next.strip('\n')]['Children'] = []
    else:
        split_line = next.split(' | ')
        parents_line = split_line[1].split(' ')
        for i in range(0, len(parents_line)):
            baysian_network[parents_line[i]]['Children'].append(split_line[0].strip())
        baysian_network[split_line[0].strip('\n')] = {}
        baysian_network[split_line[0].strip('\n')]['Parents'] = parents_line
        baysian_network[split_line[0].strip('\n')]['Children'] = []
        cond_prob = {}
        for i in range((2 ** len(parents_line))):
            conditionalProbability = input_file.readline().strip()
            splitCondProb = conditionalProbability.split(' ')
            prob = splitCondProb[0]
            truthLine = splitCondProb[1:]
            truth = tuple(True if x == '+' else False for x in truthLine)
            cond_prob[truth] = prob
        baysian_network[split_line[0].strip('\n')]['cpt'] = cond_prob
        baysian_network[split_line[0].strip('\n')]['Probability'] = []
        baysian_network[split_line[0].strip('\n')]['Type'] = 'Normal'
    first = input_file.readline()

    first = input_file.readline()
    first = ''.join(c for c in first if c not in '\n')

after_sort_variables = topological_sort(baysian_network)
o_flag = False

saveFile = open('output.txt', 'w')
saveFile.close()


def select_nodes(sorted_variables, network_dictionary, observed_variables):
    x = observed_variables.keys()
    new_network = []

    bn_values = [True if a in x else False for a in sorted_variables]

    for i in range(len(sorted_variables) ** 2):
        for v in sorted_variables:
            if bn_values[sorted_variables.index(v)] != True and any(
                            bn_values[sorted_variables.index(c)] == True for c in network_dictionary[v]['Children']):
                index = sorted_variables.index(v)
                bn_values[index] = True

    for eachNode in sorted_variables:
        if bn_values[sorted_variables.index(eachNode)]:
            new_network.append(eachNode)

    return new_network


def calculate_probability(Y, e, bayes_network):
    if bayes_network[Y]['Type'] == 'Decision':
        return 1.0

    if len(bayes_network[Y]['Parents']) == 0:
        if e[Y]:
            prob = float(bayes_network[Y]['Probability'])
            return float(bayes_network[Y]['Probability'])
        else:
            return 1.0 - float(bayes_network[Y]['Probability'])
    else:
        parents = tuple(e[p] for p in bayes_network[Y]['Parents'])
        if e[Y]:
            return float(bayes_network[Y]['cpt'][parents])
        else:
            return 1.0 - float(bayes_network[Y]['cpt'][parents])


saved_prob = {}


def get_key(Y, network, e):
    key = Y
    s = []
    for p in network[Y]['Parents']:
        key += p + '-' + str(e[p])

    child = []
    for q in network[Y]['Children']:
        if q not in child:
            child.append(q)

    for c in child:
        for w in network[c]['Children']:
            if w not in child:
                child.append(w)

    parent = []
    for c in child:
        for p in network[c]['Parents']:
            if p in e:
                parent.append(p)

    parent = sorted(parent)
    for p in parent:
        temp = p + '-' + str(e[p])
        key = key + temp

    return key


def enumerate_all(X, vars, e, bayes_network):
    global saved_prob
    if not vars:
        return 1.0

    Y = vars[0]
    k = get_key(Y, bayes_network, e)
    if k in saved_prob:
        return saved_prob[k]

    if Y in e:
        return_value = calculate_probability(Y, e, bayes_network) * enumerate_all(X, vars[1:], e, bayes_network)

    else:
        prob = []
        e2 = copy.deepcopy(e)
        for ev in [True, False]:
            e2[Y] = ev
            prob.append(calculate_probability(Y, e2, bayes_network) * enumerate_all(X, vars[1:], e2, bayes_network))

        return_value = sum(prob)
        k = get_key(Y, bayes_network, e)
        saved_prob[k] = return_value

    return return_value


for i in range(0, len(query_list)):
    global saved_prob
    X = ''
    observed_var_values = []
    query_vars = 0
    evidence_observed_dict = {}
    evidence_vars = []
    evidence_value = []
    vars = []
    value = []
    multiple_vars = []
    observed_vars = []
    observed_dic = {}
    query = query_list[i]
    split_query = query.split('(')
    function = split_query[0]
    values = split_query[1]
    flag = False

    if query[0] == 'P':
        if values.count('|') == 1:
            flag = True
            b = values[:values.index('|')]
            if b.count(",") != 0:
                c = b.split(", ")
                for i in range(0, len(c)):
                    query_vars += 1
                    vars.append(c[i][:c[i].index(' ')])
                    if c[i].count('+') == 1:
                        value.append(True)
                    else:
                        value.append(False)
            else:
                query_vars = 1
                X = b[:b.index(' ')]
                vars.append(X)
                if b.count('+') == 1:
                    value.append(True)
                else:
                    value.append(False)
            d = values[values.index('| ') + 2:]
        else:
            d = values
        e = d.split(', ')
        for i in range(0, len(e)):
            vars.append((e[i][:e[i].index(' =')]))
            if e[i].count('+') == 1:
                value.append(True)
            else:
                value.append(False)
        i = 0
        while i < len(vars):
            observed_dic[vars[i]] = value[i]
            i += 1

        bn = select_nodes(after_sort_variables, baysian_network, observed_dic)
        saved_prob = {}
        calculated_probability = enumerate_all(X, bn, observed_dic, baysian_network)
        if flag:
            X2 = ''
            evidence_vars = vars[query_vars:]
            evidence_value = value[query_vars:]
            i = 0
            while i < len(evidence_vars):
                if evidence_vars[i] != 'utility':
                    evidence_observed_dict[evidence_vars[i]] = evidence_value[i]
                i += 1
            evidence_bn = select_nodes(after_sort_variables, baysian_network, evidence_observed_dict)
            saved_prob = {}
            denominator = enumerate_all(X2, evidence_bn, evidence_observed_dict, baysian_network)
            final_result = Decimal(str(calculated_probability / denominator)).quantize(
                Decimal('.01'))
            printable_answer = final_result
        else:
            final_result = Decimal(str(calculated_probability + 1e-8)).quantize(
                Decimal('.01'))
            printable_answer = final_result
    elif query[0] == 'E':
        if values.count('|') == 1:
            flag = True
            b = values[:values.index('|')]
            if b.count(",") != 0:
                c = b.split(", ")
                for i in range(0, len(c)):
                    query_vars += 1
                    vars.append(c[i][:c[i].index(' ')])
                    if c[i].count('+') == 1:
                        value.append(True)
                    else:
                        value.append(False)
            else:
                query_vars = 1
                X = b[:b.index(' ')]
                vars.append(X)
                if b.count('+') == 1:
                    value.append(True)
                else:
                    value.append(False)
            d = values[values.index('| ') + 2:]
        else:
            d = values
        e = d.split(', ')
        for i in range(0, len(e)):
            vars.append((e[i][:e[i].index(' =')]))
            if e[i].count('+') == 1:
                value.append(True)
            else:
                value.append(False)
        # parents = bayesNetwork['utility']['Parents']
        # for i in parents:
        #     if i in e:
        #         parents.remove(i)
        #
        # tempAllValues = list(itertools.product([True, False], repeat=len(parents)))

        vars.append('utility')
        value.append(True)
        i = 0
        while i < len(vars):
            observed_dic[vars[i]] = value[i]
            i += 1
        bn = select_nodes(after_sort_variables, baysian_network,
                          observed_dic)
        saved_prob = {}
        calculated_probability = enumerate_all(X, bn, observed_dic, baysian_network)
        if flag:
            X2 = ''
            evidence_vars = vars[query_vars:]
            evidence_value = value[query_vars:]
            i = 0
            while i < len(evidence_vars):
                if evidence_vars[i] != 'utility':
                    evidence_observed_dict[evidence_vars[i]] = evidence_value[i]
                i += 1
            evidence_bn = select_nodes(after_sort_variables, baysian_network, evidence_observed_dict)
            saved_prob = {}
            denominator = enumerate_all(X2, evidence_bn, evidence_observed_dict, baysian_network)
            printable_answer = (int(round(calculated_probability / denominator)))
        else:
            printable_answer = (int(round(calculated_probability)))
    elif query[0] == 'M':
        meu_vars = []
        result_dict = {}
        if values.count('|') == 1:
            flag = True
            b = values[:values.index('|')]
            if b.count(",") != 0:
                c = b.split(", ")
                for i in range(0, len(c)):
                    b = c[i]
                    if c[i].count('=') != 0:
                        query_vars += 1
                        vars.append(c[i][:c[i].index(' ')])
                        if c[i].count('+') == 1:
                            value.append(True)
                        else:
                            value.append(False)
                    else:
                        meu_vars.append(c[i].strip())
            else:
                X = b[:b.index(' ')]
                if b.count('=') != 0:
                    query_vars = 1
                    vars.append(X)
                    if b.count('+') == 1:
                        value.append(True)
                    else:
                        value.append(False)
                else:
                    meu_vars.append(X)
            d = values[values.index('| ') + 2:]
        else:
            d = values
        e = d.split(', ')
        for i in range(0, len(e)):
            if e[i].count('=') != 0:
                vars.append((e[i][:e[i].index(' =')]))
                if e[i].count('+') == 1:
                    value.append(True)
                else:
                    value.append(False)
            else:
                meu_vars.append(e[i].strip(")"))
        vars.append('utility')
        value.append(True)
        i = 0
        while i < len(vars):
            observed_dic[vars[i]] = value[i]
            i += 1
        meu_length = len(meu_vars)
        meu_truth = list(itertools.product([True, False], repeat=meu_length))
        for i in range(0, len(meu_truth)):
            temp_evidence = copy.deepcopy(observed_dic)
            meu_value = ''
            j = 0
            for each in meu_vars:
                temp_evidence[each] = meu_truth[i][j]
                if meu_truth[i][j]:
                    meu_value += '+ '
                else:
                    meu_value += '- '
                j += 1
            bn = select_nodes(after_sort_variables, baysian_network, temp_evidence)
            saved_prob = {}
            calculated_probability = enumerate_all(X, bn, temp_evidence, baysian_network)
            if flag:
                X2 = ''
                evidence_vars = vars[query_vars:]
                evidence_value = value[query_vars:]
                i = 0
                while i < len(evidence_vars):
                    if evidence_vars[i] != 'utility':
                        evidence_observed_dict[evidence_vars[i]] = evidence_value[i]
                    i += 1
                evidence_bn = select_nodes(after_sort_variables, baysian_network, evidence_observed_dict)
                saved_prob = {}
                denominator = enumerate_all(X2, evidence_bn, evidence_observed_dict, baysian_network)
                final_result = Decimal(str(calculated_probability / denominator)).quantize(
                    Decimal('.01'))
            else:
                final_result = Decimal(str(calculated_probability)).quantize(
                    Decimal('.01'))
            result_dict[final_result] = meu_value
        answer = max(result_dict.keys())
        printable_answer = (result_dict[answer] + str(int(round(answer))))
    append = open('output.txt', 'a')
    if o_flag:
        append.write('\n')
    o_flag = True
    append.write(str(printable_answer))
    append.close()

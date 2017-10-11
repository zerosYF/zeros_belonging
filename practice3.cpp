#include<iostream>
#include<stdio.h>
#include<set>
#include<map>
#include<list>
using namespace std;

class state {//״̬�ࣻ
public:
	int num;
	map<char, state> next;
};
bool operator==(const state&s1, const state&s2) {
	if (s1.num == s2.num)return true;
	return false;//�ж�����״̬�Ƿ���ͬ��
}
bool operator<(const state &s1,const state &s2) {
	if (s1.num < s2.num) {//���������������أ�
		//setҪ����������
		return true;
	}
	return false;
}
bool operator==(const set<state>&set1, const set<state>&set2) {
	if (set1.size() != set2.size()) {
		return false;//�ж�����״̬���Ƿ���ͬ��
	}
	else {
		set<state>::iterator it1;
		set<state>::iterator it2;
		it1 = set1.begin();
		it2 = set2.begin();
		bool temp;
		for (; it1 != set1.end(), it2 != set2.end(); it1++, it2++) {
			state state1 = *it1;
			state state2 = *it2;
			temp &= (state1.num == state2.num);
			return temp;
		}
	}
}
class FA {//����״̬���ࣻ
public:
	set<char> elements;//��ĸ��
	set<state> states_s;//״̬���ϣ�
	state start_s0;//��ʼ״̬��
	set<state> end_z;//�ս�״̬����
	friend set<state> edge(set<state>,char);//״̬ת��������
};
set<state> edge(set<state> states,char m) {
	set<state> nexto;//�������
	set<state>::iterator it;
	for (it = states.begin(); it != states.end(); ++it) {//������ǰ������״̬����
		state nowstate = *it;
		map<char, state> nexts=nowstate.next;
		map<char, state>::iterator iter;
		for (iter = nexts.begin(); iter != nexts.end(); ++iter) {
			//����������״̬���е�Ԫ��������Ļ���
			if (m == iter->first) {//���������Ҫ��ľ�������
				//iter->firstָ�����iter->secondָ��ֵ��
				state mysecond = iter->second;//��������Ҫ�󻡵�״̬����������
				nexto.insert(mysecond);
			}
		}
	}
	return nexto;
}

set<state> get_eclosure(set<state> ff) {//��e�հ��ĺ�����
	set<state> result;
	set<state>::iterator it;
	for (it = ff.begin(); it != ff.end(); ++it) {
	    state thisone = (state)*it;
		result.insert(thisone);
		map<char, state> thisonenext=thisone.next;
		map<char, state> ::iterator iter;
		for (iter = thisonenext.begin(); iter != thisonenext.end(); ++iter) {
			if (iter->first == '��') {
				//result.insert(iter->second);
				result=get_eclosure(result);//�ݹ�������¸��ڵ��e�հ���
			}
		}
	}
	return result;
}
FA NtoD(FA nfa) {
	FA dfa;
	list<set<state>>ls;
	set<state>first;//��̬������ʵֻ��һ��״̬Ԫ��
	set<state>result;
	first.insert(nfa.start_s0);//����̬�������ǵĳ�̬����
	result = get_eclosure(first);//���̬��e�հ������Ϊresult����
	ls.push_back(result);

	bool temp = false;
	bool p;
	int k = 0;

	list<set<state>>::iterator lsit;
	set<state> newstatelist;
	for (lsit = ls.begin(); lsit != ls.end(); lsit++) {
		set<char>::iterator it;
		for (it = nfa.elements.begin(); it != nfa.elements.end(); it++) {
			set<state> t = edge(result, *it);//��resultÿһ�������γɵ�״̬����
			state itsnext;
			map<char, state> newmaps;
			result = get_eclosure(t);
			newmaps[*it] = itsnext;
			list<set<state>>::iterator iter;
			for (iter = ls.begin(); iter != ls.end(); iter++) {
				if (t == *iter)temp = true;
				p &= temp;
			}
			if (!p) {
				ls.push_back(result);
				state its;
				its.num = k;
				if (k == 0)dfa.start_s0 = its;
				its.next = newmaps;
				newstatelist.insert(its);
			}
		}
	}
	dfa.elements = nfa.elements;
	dfa.states_s = newstatelist;
	return dfa;
}
void divide(set<state> beingdvd) {
	set<state>::iterator it;
	set<state> one;
	set<state> two;
	for (it = beingdvd.begin(); it != beingdvd.end(); it++) {
		state thisone = *it;
		map<char, state>nexts = thisone.next;
		map<char, state>::iterator iter;
		bool belonged = false;
		for (iter = nexts.begin(); iter != nexts.end(); iter++) {
			int nextnum = iter->first;
			set<state>::iterator innerit;
			bool belonged = false;
			for (innerit = beingdvd.begin(); innerit != beingdvd.end(); innerit++) {
				state again = *innerit;
				if (nextnum == again.num) {
					belonged == true;
					break;
				}
			}
			if (belonged)break;
		}
		if (!belonged) {
			one.insert(thisone);
			divide(one);//�ݹ���������ֵļ����ٻ��֣�
		}
		else {
			two.insert(thisone);
			divide(two);
		}
	}
}
FA minimize(FA dfa) {
	FA mindfa;
	set <state> ends = dfa.end_z;
	set<state> states = dfa.states_s;
	set<state> notends;
	set<state>::iterator endit;
	set<state>::iterator statesit;
	for (statesit = states.begin(); statesit != states.end(); statesit++) {
		bool isend = false;
		for (endit = ends.begin(); endit != ends.end(); endit++) {
			if ((state)*endit == (state)*statesit) {
				isend = true;
			}
		}
		if(!isend)
		notends.insert(*statesit);
	}
	//�����Ƿ�Ϊ�սἯ���������֣�
	divide(ends);//����divide�����������֣�
	divide(notends);
	return mindfa;
}
int main() {
	return 0;
}
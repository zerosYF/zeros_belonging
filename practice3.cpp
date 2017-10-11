#include<iostream>
#include<stdio.h>
#include<set>
#include<map>
#include<list>
using namespace std;

class state {//状态类；
public:
	int num;
	map<char, state> next;
};
bool operator==(const state&s1, const state&s2) {
	if (s1.num == s2.num)return true;
	return false;//判定两个状态是否相同；
}
bool operator<(const state &s1,const state &s2) {
	if (s1.num < s2.num) {//必须进行运算符重载；
		//set要进行弱排序；
		return true;
	}
	return false;
}
bool operator==(const set<state>&set1, const set<state>&set2) {
	if (set1.size() != set2.size()) {
		return false;//判定两个状态集是否相同；
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
class FA {//有限状态机类；
public:
	set<char> elements;//字母表；
	set<state> states_s;//状态集合；
	state start_s0;//开始状态；
	set<state> end_z;//终结状态集；
	friend set<state> edge(set<state>,char);//状态转换函数；
};
set<state> edge(set<state> states,char m) {
	set<state> nexto;//结果集；
	set<state>::iterator it;
	for (it = states.begin(); it != states.end(); ++it) {//遍历当前所给的状态集；
		state nowstate = *it;
		map<char, state> nexts=nowstate.next;
		map<char, state>::iterator iter;
		for (iter = nexts.begin(); iter != nexts.end(); ++iter) {
			//遍历由所给状态集中的元素所射出的弧；
			if (m == iter->first) {//如果是我们要求的经过弧；
				//iter->first指向键；iter->second指向值；
				state mysecond = iter->second;//将经过所要求弧的状态放入结果集；
				nexto.insert(mysecond);
			}
		}
	}
	return nexto;
}

set<state> get_eclosure(set<state> ff) {//求e闭包的函数；
	set<state> result;
	set<state>::iterator it;
	for (it = ff.begin(); it != ff.end(); ++it) {
	    state thisone = (state)*it;
		result.insert(thisone);
		map<char, state> thisonenext=thisone.next;
		map<char, state> ::iterator iter;
		for (iter = thisonenext.begin(); iter != thisonenext.end(); ++iter) {
			if (iter->first == 'ε') {
				//result.insert(iter->second);
				result=get_eclosure(result);//递归继续求下个节点的e闭包；
			}
		}
	}
	return result;
}
FA NtoD(FA nfa) {
	FA dfa;
	list<set<state>>ls;
	set<state>first;//初态集，其实只有一个状态元；
	set<state>result;
	first.insert(nfa.start_s0);//将初态放入我们的初态集；
	result = get_eclosure(first);//求初态的e闭包；结果为result集；
	ls.push_back(result);

	bool temp = false;
	bool p;
	int k = 0;

	list<set<state>>::iterator lsit;
	set<state> newstatelist;
	for (lsit = ls.begin(); lsit != ls.end(); lsit++) {
		set<char>::iterator it;
		for (it = nfa.elements.begin(); it != nfa.elements.end(); it++) {
			set<state> t = edge(result, *it);//对result每一个弧所形成的状态集；
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
			divide(one);//递归继续对所分的集合再划分；
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
	//根据是否为终结集做基本划分；
	divide(ends);//调用divide函数继续划分；
	divide(notends);
	return mindfa;
}
int main() {
	return 0;
}
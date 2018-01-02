#pragma once
#include<d3dx9.h>
#include<windows.h>
namespace d3d {
	bool InitD3D(//���ڵĳ�ʼ����
		HINSTANCE hInstance,
		int width,
		int height,
		bool windowed,
		D3DDEVTYPE devicetype,
		IDirect3DDevice9 ** device);

	int EnterMsgLoop(bool (*ptr_display)(float timedelta));//��Ϣѭ����

	LRESULT CALLBACK WndProc(//�ص�������
		HWND hWnd,
		UINT msg,
		WPARAM wParam,
		LPARAM lParam);

	template<class T> void Release(T t) {
		if (t) {//�ͷ�COM�����
			t->Release();
			t = 0;
		}
	}

	template<class T> void Delete(T t) {
		if (t) {//ɾ�����ɶ��еĶ���;
			delete t;
			t = 0;
		}
	}
}

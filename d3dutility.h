#pragma once
#include<d3dx9.h>
#include<windows.h>
namespace d3d {
	bool InitD3D(//窗口的初始化；
		HINSTANCE hInstance,
		int width,
		int height,
		bool windowed,
		D3DDEVTYPE devicetype,
		IDirect3DDevice9 ** device);

	int EnterMsgLoop(bool (*ptr_display)(float timedelta));//消息循环；

	LRESULT CALLBACK WndProc(//回调方法；
		HWND hWnd,
		UINT msg,
		WPARAM wParam,
		LPARAM lParam);

	template<class T> void Release(T t) {
		if (t) {//释放COM组件；
			t->Release();
			t = 0;
		}
	}

	template<class T> void Delete(T t) {
		if (t) {//删除自由堆中的对象;
			delete t;
			t = 0;
		}
	}
}

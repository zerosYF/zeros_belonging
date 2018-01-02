#include"d3dutility.h"
#include<tchar.h>
namespace d3d {
	bool d3d::InitD3D(
		HINSTANCE hInstance,int width, int height,
		bool windowed,D3DDEVTYPE devicetype,IDirect3DDevice9 **device) {
		HWND hWnd; //窗口句柄；
		WNDCLASS wndclass;//窗口类别，在创建窗口之前需要register；
		wndclass.style = CS_HREDRAW | CS_VREDRAW;
		wndclass.lpfnWndProc = (WNDPROC)d3d::WndProc;
		wndclass.cbClsExtra = 0;
		wndclass.cbWndExtra = 0;
		wndclass.hInstance = hInstance;
		wndclass.hIcon = LoadIcon(NULL,IDI_APPLICATION);
		wndclass.hCursor = LoadCursor(NULL,IDC_ARROW);
		wndclass.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);
		wndclass.lpszMenuName = NULL;
		wndclass.lpszClassName = _T("Direct3dApp");

		if (!RegisterClass(&wndclass)) {
			MessageBox(0,_T("this app requires windows NT"),0,0);
			return false;
		}

		hWnd = CreateWindow(
			_T("Direct3dApp"),_T("Direct3dApp"),
			WS_EX_TOPMOST,0,0,width,height,
			0,0,hInstance,0);
		::ShowWindow(hWnd,SW_SHOW);
		::UpdateWindow(hWnd);

		IDirect3D9 *_d3d9;
		_d3d9 = Direct3DCreate9(D3D_SDK_VERSION);

		if (!_d3d9) {
			MessageBox(0,_T("Created3d9--failed"),0,0);
			return false;
		}

		D3DCAPS9 caps;
		_d3d9->GetDeviceCaps(D3DADAPTER_DEFAULT,D3DDEVTYPE_HAL,&caps);
		int vp;
		if (caps.DevCaps&D3DDEVCAPS_HWTRANSFORMANDLIGHT) {
			vp = D3DCREATE_HARDWARE_VERTEXPROCESSING;
		}
		else {
			vp = D3DCREATE_SOFTWARE_VERTEXPROCESSING;
		}

		D3DPRESENT_PARAMETERS d3dpm;
		::ZeroMemory(&d3dpm,sizeof(D3DPRESENT_PARAMETERS));
		d3dpm.BackBufferWidth = width;
		d3dpm.BackBufferHeight = height;
		d3dpm.BackBufferFormat = D3DFMT_UNKNOWN;
		d3dpm.BackBufferCount = 1;
		d3dpm.MultiSampleType = D3DMULTISAMPLE_NONE;
		d3dpm.MultiSampleQuality = 0;
		d3dpm.SwapEffect = D3DSWAPEFFECT_DISCARD;
		d3dpm.hDeviceWindow = hWnd;
		d3dpm.Windowed = windowed;
		d3dpm.EnableAutoDepthStencil = true;
		d3dpm.AutoDepthStencilFormat = D3DFMT_D24S8;
		d3dpm.Flags = 0;
		d3dpm.FullScreen_RefreshRateInHz = D3DPRESENT_RATE_DEFAULT;
		d3dpm.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;

		HRESULT hr = _d3d9->CreateDevice(
			D3DADAPTER_DEFAULT,
			D3DDEVTYPE_HAL,
			hWnd,vp,&d3dpm,device);
		if (FAILED(hr)) {
			::MessageBox(0,_T("CreateDevice--Failed"),0,0);
			return false;
		}

		return true;

	}

	int d3d::EnterMsgLoop(bool(*ptr_display)(float timedelta)) {
		MSG msg;
		::ZeroMemory(&msg, sizeof(MSG));

		static float lasttime = (float)timeGetTime();

		while (msg.message != WM_QUIT) {
			if (::PeekMessage(&msg, 0, 0, 0, PM_REMOVE)) {
				::TranslateMessage(&msg);
				::DispatchMessage(&msg);
			}
			else {
				float currenttime = (float)timeGetTime();
				float timeDelta = (currenttime - lasttime)*0.001f;
				ptr_display(timeDelta);

				lasttime = currenttime;
			}
		}
		return msg.wParam;
	}

	LRESULT CALLBACK d3d::WndProc(HWND hWnd, UINT msg,
		WPARAM wParam, LPARAM lParam) {
		switch (msg) {
		case WM_DESTROY:
			::PostQuitMessage(0);
			break;

		case WM_KEYDOWN:
			if (wParam == VK_ESCAPE) {
				::DestroyWindow(hWnd);
				break;
			}
		}

		return ::DefWindowProc(hWnd, msg, wParam, lParam);
	}

}
IDirect3DDevice9 *device = 0;
bool windowed = true;
bool Setup() {
	return true;
}
void Clearup() {

}

bool Display(float timedelta) {
	if (device) {
		device->Clear(0, 0,//矩形数目与矩形数组；
			D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,//后台缓存和深度或模板缓存；
			0x00000000, 1.0f, 0);
		device->Present(0, 0, 0, 0);
	}
	return true;
}
int WINAPI WinMain(
	HINSTANCE hInstance,
	HINSTANCE preInstance, PSTR cmdline, int showcmd) {

	if (!d3d::InitD3D(hInstance, 800, 600, true, D3DDEVTYPE_HAL, &device)) {
		::MessageBox(0, _T("Initd3d--failed"), 0, 0);
		return 0;
	}

	if (!Setup()) {
		::MessageBox(0, _T("Setup--failed"), 0, 0);
		return 0;
	}

	d3d::EnterMsgLoop(Display);

	Clearup();
	device->Release();
	return 0;
}
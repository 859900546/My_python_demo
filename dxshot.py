# ----------------------------------截图区块----------------------------------
import win32api
import win32con
import ctypes
import ctypes.wintypes as wintypes
import comtypes
import enum
import numpy as np
from typing import Tuple
from threading import Event, Lock
from numpy import rot90
from numpy.ctypeslib import as_array
from dataclasses import InitVar
from dataclasses import dataclass
from typing import List

MONITORINFOF_PRIMARY = 0x00000001
DISPLAY_DEVICE_ACTIVE = 1
DISPLAY_DEVICE_PRIMARY_DEVICE = 4

DXGI_ERROR_ACCESS_LOST = 0x887A0026
DXGI_ERROR_NOT_FOUND = 0x887A0002
DXGI_ERROR_WAIT_TIMEOUT = 0x887A0027
ABANDONED_MUTEX_EXCEPTION = -0x7785ffda  # -2005270490

D3D11_CPU_ACCESS_WRITE = 0x10000
D3D11_CPU_ACCESS_READ = 0x20000

D3D_FEATURE_LEVEL_9_1 = 0x9100
D3D_FEATURE_LEVEL_9_2 = 0x9200
D3D_FEATURE_LEVEL_9_3 = 0x9300
D3D_FEATURE_LEVEL_10_0 = 0xA000
D3D_FEATURE_LEVEL_10_1 = 0xA100
D3D_FEATURE_LEVEL_11_0 = 0xB000
D3D_FEATURE_LEVEL_11_1 = 0xB100

D3D11_USAGE_DEFAULT = 0
D3D11_USAGE_IMMUTABLE = 1
D3D11_USAGE_DYNAMIC = 2
D3D11_USAGE_STAGING = 3

DXGI_FORMAT_B8G8R8A8_UNORM = 87


class DXGI_SAMPLE_DESC(ctypes.Structure):
    _fields_ = [
        ("Count", wintypes.UINT),
        ("Quality", wintypes.UINT),
    ]


class D3D11_BOX(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.UINT),
        ("top", wintypes.UINT),
        ("front", wintypes.UINT),
        ("right", wintypes.UINT),
        ("bottom", wintypes.UINT),
        ("back", wintypes.UINT),
    ]


class D3D11_TEXTURE2D_DESC(ctypes.Structure):
    _fields_ = [
        ("Width", wintypes.UINT),
        ("Height", wintypes.UINT),
        ("MipLevels", wintypes.UINT),
        ("ArraySize", wintypes.UINT),
        ("Format", wintypes.UINT),
        ("SampleDesc", DXGI_SAMPLE_DESC),
        ("Usage", wintypes.UINT),
        ("BindFlags", wintypes.UINT),
        ("CPUAccessFlags", wintypes.UINT),
        ("MiscFlags", wintypes.UINT),
    ]


class ID3D11DeviceChild(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{1841e5c8-16b0-489b-bcc8-44cfb0d5deae}")
    _methods_ = [
        comtypes.STDMETHOD(None, "GetDevice"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetPrivateData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetPrivateData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetPrivateDataInterface"),
    ]


class ID3D11Resource(ID3D11DeviceChild):
    _iid_ = comtypes.GUID("{dc8e63f3-d12b-4952-b47b-5e45026a862d}")
    _methods_ = [
        comtypes.STDMETHOD(None, "GetType"),
        comtypes.STDMETHOD(None, "SetEvictionPriority"),
        comtypes.STDMETHOD(wintypes.UINT, "GetEvictionPriority"),
    ]


class ID3D11Texture2D(ID3D11Resource):
    _iid_ = comtypes.GUID("{6f15aaf2-d208-4e89-9ab4-489535d34f9c}")
    _methods_ = [
        comtypes.STDMETHOD(None, "GetDesc", [ctypes.POINTER(D3D11_TEXTURE2D_DESC)]),
    ]


class ID3D11DeviceContext(ID3D11DeviceChild):
    _iid_ = comtypes.GUID("{c0bfa96c-e089-44fb-8eaf-26f8796190da}")
    _methods_ = [
        comtypes.STDMETHOD(None, "VSSetConstantBuffers"),
        comtypes.STDMETHOD(None, "PSSetShaderResources"),
        comtypes.STDMETHOD(None, "PSSetShader"),
        comtypes.STDMETHOD(None, "PSSetSamplers"),
        comtypes.STDMETHOD(None, "VSSetShader"),
        comtypes.STDMETHOD(None, "DrawIndexed"),
        comtypes.STDMETHOD(None, "Draw"),
        comtypes.STDMETHOD(comtypes.HRESULT, "Map"),
        comtypes.STDMETHOD(None, "Unmap"),
        comtypes.STDMETHOD(None, "PSSetConstantBuffers"),
        comtypes.STDMETHOD(None, "IASetInputLayout"),
        comtypes.STDMETHOD(None, "IASetVertexBuffers"),
        comtypes.STDMETHOD(None, "IASetIndexBuffer"),
        comtypes.STDMETHOD(None, "DrawIndexedInstanced"),
        comtypes.STDMETHOD(None, "DrawInstanced"),
        comtypes.STDMETHOD(None, "GSSetConstantBuffers"),
        comtypes.STDMETHOD(None, "GSSetShader"),
        comtypes.STDMETHOD(None, "IASetPrimitiveTopology"),
        comtypes.STDMETHOD(None, "VSSetShaderResources"),
        comtypes.STDMETHOD(None, "VSSetSamplers"),
        comtypes.STDMETHOD(None, "Begin"),
        comtypes.STDMETHOD(None, "End"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetData"),
        comtypes.STDMETHOD(None, "SetPredication"),
        comtypes.STDMETHOD(None, "GSSetShaderResources"),
        comtypes.STDMETHOD(None, "GSSetSamplers"),
        comtypes.STDMETHOD(None, "OMSetRenderTargets"),
        comtypes.STDMETHOD(None, "OMSetRenderTargetsAndUnorderedAccessViews"),
        comtypes.STDMETHOD(None, "OMSetBlendState"),
        comtypes.STDMETHOD(None, "OMSetDepthStencilState"),
        comtypes.STDMETHOD(None, "SOSetTargets"),
        comtypes.STDMETHOD(None, "DrawAuto"),
        comtypes.STDMETHOD(None, "DrawIndexedInstancedIndirect"),
        comtypes.STDMETHOD(None, "DrawInstancedIndirect"),
        comtypes.STDMETHOD(None, "Dispatch"),
        comtypes.STDMETHOD(None, "DispatchIndirect"),
        comtypes.STDMETHOD(None, "RSSetState"),
        comtypes.STDMETHOD(None, "RSSetViewports"),
        comtypes.STDMETHOD(None, "RSSetScissorRects"),
        comtypes.STDMETHOD(
            None,
            "CopySubresourceRegion",
            [
                ctypes.POINTER(ID3D11Resource),
                wintypes.UINT,
                wintypes.UINT,
                wintypes.UINT,
                wintypes.UINT,
                ctypes.POINTER(ID3D11Resource),
                wintypes.UINT,
                ctypes.POINTER(D3D11_BOX),
            ],
        ),
        comtypes.STDMETHOD(
            None,
            "CopyResource",
            [ctypes.POINTER(ID3D11Resource), ctypes.POINTER(ID3D11Resource)],
        ),
        comtypes.STDMETHOD(None, "UpdateSubresource"),
        comtypes.STDMETHOD(None, "CopyStructureCount"),
        comtypes.STDMETHOD(None, "ClearRenderTargetView"),
        comtypes.STDMETHOD(None, "ClearUnorderedAccessViewUint"),
        comtypes.STDMETHOD(None, "ClearUnorderedAccessViewFloat"),
        comtypes.STDMETHOD(None, "ClearDepthStencilView"),
        comtypes.STDMETHOD(None, "GenerateMips"),
        comtypes.STDMETHOD(None, "SetResourceMinLOD"),
        comtypes.STDMETHOD(wintypes.FLOAT, "GetResourceMinLOD"),
        comtypes.STDMETHOD(None, "ResolveSubresource"),
        comtypes.STDMETHOD(None, "ExecuteCommandList"),
        comtypes.STDMETHOD(None, "HSSetShaderResources"),
        comtypes.STDMETHOD(None, "HSSetShader"),
        comtypes.STDMETHOD(None, "HSSetSamplers"),
        comtypes.STDMETHOD(None, "HSSetConstantBuffers"),
        comtypes.STDMETHOD(None, "DSSetShaderResources"),
        comtypes.STDMETHOD(None, "DSSetShader"),
        comtypes.STDMETHOD(None, "DSSetSamplers"),
        comtypes.STDMETHOD(None, "DSSetConstantBuffers"),
        comtypes.STDMETHOD(None, "CSSetShaderResources"),
        comtypes.STDMETHOD(None, "CSSetUnorderedAccessViews"),
        comtypes.STDMETHOD(None, "CSSetShader"),
        comtypes.STDMETHOD(None, "CSSetSamplers"),
        comtypes.STDMETHOD(None, "CSSetConstantBuffers"),
        comtypes.STDMETHOD(None, "VSGetConstantBuffers"),
        comtypes.STDMETHOD(None, "PSGetShaderResources"),
        comtypes.STDMETHOD(None, "PSGetShader"),
        comtypes.STDMETHOD(None, "PSGetSamplers"),
        comtypes.STDMETHOD(None, "VSGetShader"),
        comtypes.STDMETHOD(None, "PSGetConstantBuffers"),
        comtypes.STDMETHOD(None, "IAGetInputLayout"),
        comtypes.STDMETHOD(None, "IAGetVertexBuffers"),
        comtypes.STDMETHOD(None, "IAGetIndexBuffer"),
        comtypes.STDMETHOD(None, "GSGetConstantBuffers"),
        comtypes.STDMETHOD(None, "GSGetShader"),
        comtypes.STDMETHOD(None, "IAGetPrimitiveTopology"),
        comtypes.STDMETHOD(None, "VSGetShaderResources"),
        comtypes.STDMETHOD(None, "VSGetSamplers"),
        comtypes.STDMETHOD(None, "GetPredication"),
        comtypes.STDMETHOD(None, "GSGetShaderResources"),
        comtypes.STDMETHOD(None, "GSGetSamplers"),
        comtypes.STDMETHOD(None, "OMGetRenderTargets"),
        comtypes.STDMETHOD(None, "OMGetRenderTargetsAndUnorderedAccessViews"),
        comtypes.STDMETHOD(None, "OMGetBlendState"),
        comtypes.STDMETHOD(None, "OMGetDepthStencilState"),
        comtypes.STDMETHOD(None, "SOGetTargets"),
        comtypes.STDMETHOD(None, "RSGetState"),
        comtypes.STDMETHOD(None, "RSGetViewports"),
        comtypes.STDMETHOD(None, "RSGetScissorRects"),
        comtypes.STDMETHOD(None, "HSGetShaderResources"),
        comtypes.STDMETHOD(None, "HSGetShader"),
        comtypes.STDMETHOD(None, "HSGetSamplers"),
        comtypes.STDMETHOD(None, "HSGetConstantBuffers"),
        comtypes.STDMETHOD(None, "DSGetShaderResources"),
        comtypes.STDMETHOD(None, "DSGetShader"),
        comtypes.STDMETHOD(None, "DSGetSamplers"),
        comtypes.STDMETHOD(None, "DSGetConstantBuffers"),
        comtypes.STDMETHOD(None, "CSGetShaderResources"),
        comtypes.STDMETHOD(None, "CSGetUnorderedAccessViews"),
        comtypes.STDMETHOD(None, "CSGetShader"),
        comtypes.STDMETHOD(None, "CSGetSamplers"),
        comtypes.STDMETHOD(None, "CSGetConstantBuffers"),
        comtypes.STDMETHOD(None, "ClearState"),
        comtypes.STDMETHOD(None, "Flush"),
        comtypes.STDMETHOD(None, "GetType"),
        comtypes.STDMETHOD(wintypes.UINT, "GetContextFlags"),
        comtypes.STDMETHOD(comtypes.HRESULT, "FinishCommandList"),
    ]


class ID3D11Device(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{db6f6ddb-ac77-4e88-8253-819df9bbf140}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateBuffer"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateTexture1D"),
        comtypes.STDMETHOD(
            comtypes.HRESULT,
            "CreateTexture2D",
            [
                ctypes.POINTER(D3D11_TEXTURE2D_DESC),
                ctypes.POINTER(None),
                ctypes.POINTER(ctypes.POINTER(ID3D11Texture2D)),
            ],
        ),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateTexture3D"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateShaderResourceView"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateUnorderedAccessView"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateRenderTargetView"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateDepthStencilView"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateInputLayout"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateVertexShader"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateGeometryShader"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateGeometryShaderWithStreamOutput"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreatePixelShader"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateHullShader"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateDomainShader"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateComputeShader"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateClassLinkage"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateBlendState"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateDepthStencilState"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateRasterizerState"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateSamplerState"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateQuery"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreatePredicate"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateCounter"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateDeferredContext"),
        comtypes.STDMETHOD(comtypes.HRESULT, "OpenSharedResource"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CheckFormatSupport"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CheckMultisampleQualityLevels"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CheckCounterInfo"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CheckCounter"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CheckFeatureSupport"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetPrivateData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetPrivateData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetPrivateDataInterface"),
        comtypes.STDMETHOD(ctypes.c_int32, "GetFeatureLevel"),
        comtypes.STDMETHOD(ctypes.c_uint, "GetCreationFlags"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDeviceRemovedReason"),
        comtypes.STDMETHOD(
            None,
            "GetImmediateContext",
            [ctypes.POINTER(ctypes.POINTER(ID3D11DeviceContext))],
        ),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetExceptionMode"),
        comtypes.STDMETHOD(ctypes.c_uint, "GetExceptionMode"),
    ]


class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]


class DXGI_ADAPTER_DESC1(ctypes.Structure):
    _fields_ = [
        ("Description", wintypes.WCHAR * 128),
        ("VendorId", wintypes.UINT),
        ("DeviceId", wintypes.UINT),
        ("SubSysId", wintypes.UINT),
        ("Revision", wintypes.UINT),
        ("DedicatedVideoMemory", wintypes.ULARGE_INTEGER),
        ("DedicatedSystemMemory", wintypes.ULARGE_INTEGER),
        ("SharedSystemMemory", wintypes.ULARGE_INTEGER),
        ("AdapterLuid", LUID),
        ("Flags", wintypes.UINT),
    ]


class DXGI_OUTPUT_DESC(ctypes.Structure):
    _fields_ = [
        ("DeviceName", wintypes.WCHAR * 32),
        ("DesktopCoordinates", wintypes.RECT),
        ("AttachedToDesktop", wintypes.BOOL),
        ("Rotation", wintypes.UINT),
        ("Monitor", wintypes.HMONITOR),
    ]


class DXGI_OUTDUPL_POINTER_POSITION(ctypes.Structure):
    _fields_ = [("Position", wintypes.POINT), ("Visible", wintypes.BOOL)]


class DXGI_OUTDUPL_FRAME_INFO(ctypes.Structure):
    _fields_ = [
        ("LastPresentTime", wintypes.LARGE_INTEGER),
        ("LastMouseUpdateTime", wintypes.LARGE_INTEGER),
        ("AccumulatedFrames", wintypes.UINT),
        ("RectsCoalesced", wintypes.BOOL),
        ("ProtectedContentMaskedOut", wintypes.BOOL),
        ("PointerPosition", DXGI_OUTDUPL_POINTER_POSITION),
        ("TotalMetadataBufferSize", wintypes.UINT),
        ("PointerShapeBufferSize", wintypes.UINT),
    ]


class DXGI_MAPPED_RECT(ctypes.Structure):
    _fields_ = [("Pitch", wintypes.INT), ("pBits", ctypes.POINTER(wintypes.FLOAT))]


class IDXGIObject(comtypes.IUnknown):
    _iid_ = comtypes.GUID("{aec22fb8-76f3-4639-9be0-28eb43a67a2e}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "SetPrivateData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetPrivateDataInterface"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetPrivateData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetParent"),
    ]


class IDXGIDeviceSubObject(IDXGIObject):
    _iid_ = comtypes.GUID("{3d3e0379-f9de-4d58-bb6c-18d62992f1a6}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDevice"),
    ]


class IDXGIResource(IDXGIDeviceSubObject):
    _iid_ = comtypes.GUID("{035f3ab4-482e-4e50-b41f-8a7f8bd8960b}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "GetSharedHandle"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetUsage"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetEvictionPriority"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetEvictionPriority"),
    ]


class IDXGISurface(IDXGIDeviceSubObject):
    _iid_ = comtypes.GUID("{cafcb56c-6ac3-4889-bf47-9e23bbd260ec}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDesc"),
        comtypes.STDMETHOD(
            comtypes.HRESULT, "Map", [ctypes.POINTER(DXGI_MAPPED_RECT), wintypes.UINT]
        ),
        comtypes.STDMETHOD(comtypes.HRESULT, "Unmap"),
    ]


class IDXGIOutputDuplication(IDXGIObject):
    _iid_ = comtypes.GUID("{191cfac3-a341-470d-b26e-a864f428319c}")
    _methods_ = [
        comtypes.STDMETHOD(None, "GetDesc"),
        comtypes.STDMETHOD(
            comtypes.HRESULT,
            "AcquireNextFrame",
            [
                wintypes.UINT,
                ctypes.POINTER(DXGI_OUTDUPL_FRAME_INFO),
                ctypes.POINTER(ctypes.POINTER(IDXGIResource)),
            ],
        ),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetFrameDirtyRects"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetFrameMoveRects"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetFramePointerShape"),
        comtypes.STDMETHOD(comtypes.HRESULT, "MapDesktopSurface"),
        comtypes.STDMETHOD(comtypes.HRESULT, "UnMapDesktopSurface"),
        comtypes.STDMETHOD(comtypes.HRESULT, "ReleaseFrame"),
    ]


class IDXGIOutput(IDXGIObject):
    _iid_ = comtypes.GUID("{ae02eedb-c735-4690-8d52-5a8dc20213aa}")
    _methods_ = [
        comtypes.STDMETHOD(
            comtypes.HRESULT, "GetDesc", [ctypes.POINTER(DXGI_OUTPUT_DESC)]
        ),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDisplayModeList"),
        comtypes.STDMETHOD(comtypes.HRESULT, "FindClosestMatchingMode"),
        comtypes.STDMETHOD(comtypes.HRESULT, "WaitForVBlank"),
        comtypes.STDMETHOD(comtypes.HRESULT, "TakeOwnership"),
        comtypes.STDMETHOD(None, "ReleaseOwnership"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetGammaControlCapabilities"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetGammaControl"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetGammaControl"),
        comtypes.STDMETHOD(comtypes.HRESULT, "SetDisplaySurface"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDisplaySurfaceData"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetFrameStatistics"),
    ]


class IDXGIOutput1(IDXGIOutput):
    _iid_ = comtypes.GUID("{00cddea8-939b-4b83-a340-a685226666cc}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDisplayModeList1"),
        comtypes.STDMETHOD(comtypes.HRESULT, "FindClosestMatchingMode1"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDisplaySurfaceData1"),
        comtypes.STDMETHOD(
            comtypes.HRESULT,
            "DuplicateOutput",
            [
                ctypes.POINTER(ID3D11Device),
                ctypes.POINTER(ctypes.POINTER(IDXGIOutputDuplication)),
            ],
        ),
    ]


class IDXGIAdapter(IDXGIObject):
    _iid_ = comtypes.GUID("{2411e7e1-12ac-4ccf-bd14-9798e8534dc0}")
    _methods_ = [
        comtypes.STDMETHOD(
            comtypes.HRESULT,
            "EnumOutputs",
            [wintypes.UINT, ctypes.POINTER(ctypes.POINTER(IDXGIOutput))],
        ),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetDesc"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CheckInterfaceSupport"),
    ]


class IDXGIAdapter1(IDXGIAdapter):
    _iid_ = comtypes.GUID("{29038f61-3839-4626-91fd-086879011a05}")
    _methods_ = [
        comtypes.STDMETHOD(
            comtypes.HRESULT, "GetDesc1", [ctypes.POINTER(DXGI_ADAPTER_DESC1)]
        ),
    ]


class IDXGIFactory(IDXGIObject):
    _iid_ = comtypes.GUID("{7b7166ec-21c7-44ae-b21a-c9ae321ae369}")
    _methods_ = [
        comtypes.STDMETHOD(comtypes.HRESULT, "EnumAdapters"),
        comtypes.STDMETHOD(comtypes.HRESULT, "MakeWindowAssociation"),
        comtypes.STDMETHOD(comtypes.HRESULT, "GetWindowAssociation"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateSwapChain"),
        comtypes.STDMETHOD(comtypes.HRESULT, "CreateSoftwareAdapter"),
    ]


class IDXGIFactory1(IDXGIFactory):
    _iid_ = comtypes.GUID("{770aae78-f26f-4dba-a829-253c83d1b387}")
    _methods_ = [
        comtypes.STDMETHOD(
            comtypes.HRESULT,
            "EnumAdapters1",
            [ctypes.c_uint, ctypes.POINTER(ctypes.POINTER(IDXGIAdapter1))],
        ),
        comtypes.STDMETHOD(wintypes.BOOL, "IsCurrent"),
    ]


class DISPLAY_DEVICE(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]


@dataclass
class Device:
    adapter: ctypes.POINTER(IDXGIAdapter1)
    device: ctypes.POINTER(ID3D11Device) = None
    context: ctypes.POINTER(ID3D11DeviceContext) = None
    im_context: ctypes.POINTER(ID3D11DeviceContext) = None
    desc: DXGI_ADAPTER_DESC1 = None

    def __post_init__(self) -> None:
        self.desc = DXGI_ADAPTER_DESC1()
        self.adapter.GetDesc1(ctypes.byref(self.desc))

        D3D11CreateDevice = ctypes.windll.d3d11.D3D11CreateDevice

        feature_levels = [
            D3D_FEATURE_LEVEL_11_0,
            D3D_FEATURE_LEVEL_10_1,
            D3D_FEATURE_LEVEL_10_0,
        ]

        self.device = ctypes.POINTER(ID3D11Device)()
        self.context = ctypes.POINTER(ID3D11DeviceContext)()
        self.im_context = ctypes.POINTER(ID3D11DeviceContext)()

        D3D11CreateDevice(
            self.adapter,
            0,
            None,
            0,
            ctypes.byref((ctypes.c_uint * len(feature_levels))(*feature_levels)),
            len(feature_levels),
            7,
            ctypes.byref(self.device),
            None,
            ctypes.byref(self.context),
        )
        self.device.GetImmediateContext(ctypes.byref(self.im_context))

    def enum_outputs(self) -> List[ctypes.POINTER(IDXGIOutput1)]:
        i = 0
        p_outputs = []
        while True:
            try:
                p_output = ctypes.POINTER(IDXGIOutput1)()
                self.adapter.EnumOutputs(i, ctypes.byref(p_output))
                p_outputs.append(p_output)
                i += 1
            except comtypes.COMError as ce:
                if ctypes.c_int32(DXGI_ERROR_NOT_FOUND).value == ce.args[0]:
                    break
                else:
                    raise ce
        return p_outputs


@dataclass
class Output:
    output: ctypes.POINTER(IDXGIOutput1)
    rotation_mapping: tuple = (0, 0, 90, 180, 270)
    desc: DXGI_OUTPUT_DESC = None

    def __post_init__(self):
        self.desc = DXGI_OUTPUT_DESC()
        self.update_desc()

    def update_desc(self):
        if self.desc is None:
            self.desc = DXGI_OUTPUT_DESC()
        self.output.GetDesc(ctypes.byref(self.desc))

    @property
    def hmonitor(self) -> wintypes.HMONITOR:
        return self.desc.Monitor

    @property
    def devicename(self) -> str:
        return self.desc.DeviceName

    @property
    def resolution(self) -> Tuple[int, int]:
        return (
            (self.desc.DesktopCoordinates.right - self.desc.DesktopCoordinates.left),
            (self.desc.DesktopCoordinates.bottom - self.desc.DesktopCoordinates.top),
        )

    @property
    def surface_size(self) -> Tuple[int, int]:
        if self.rotation_angle in (90, 270):
            return self.resolution[1], self.resolution[0]
        else:
            return self.resolution

    @property
    def attached_to_desktop(self) -> bool:
        return bool(self.desc.AttachedToDesktop)

    @property
    def rotation_angle(self) -> int:
        return self.rotation_mapping[self.desc.Rotation]

    def __repr__(self) -> str:
        return "<{} Name:{} Resolution:{} Rotation:{}>".format(
            self.__class__.__name__,
            self.devicename,
            self.resolution,
            self.rotation_angle,
        )


@dataclass
class Duplicator:
    texture: ctypes.POINTER(ID3D11Texture2D) = ctypes.POINTER(ID3D11Texture2D)()
    duplicator: ctypes.POINTER(IDXGIOutputDuplication) = None
    updated: bool = False
    output: InitVar[Output] = None
    device: InitVar[Device] = None

    def __post_init__(self, output: Output, device: Device) -> None:
        self.duplicator = ctypes.POINTER(IDXGIOutputDuplication)()
        print(device.device, ctypes.byref(self.duplicator))
        output.output.DuplicateOutput(device.device, ctypes.byref(self.duplicator))

    def update_frame(self):

        info = DXGI_OUTDUPL_FRAME_INFO()
        res = ctypes.POINTER(IDXGIResource)()

        try:
            self.duplicator.AcquireNextFrame(
                0,
                ctypes.byref(info),
                ctypes.byref(res),
            )
        except comtypes.COMError as ce:
            if ctypes.c_int32(DXGI_ERROR_ACCESS_LOST).value == ce.args[0]:
                del self.duplicator
                raise ce
            if ctypes.c_int32(DXGI_ERROR_WAIT_TIMEOUT).value == ce.args[0]:
                self.updated = False
                return True
            else:
                raise ce

        self.texture = res.QueryInterface(ID3D11Texture2D)
        self.updated = True

        return True

    def release_frame(self):
        self.duplicator.ReleaseFrame()


@dataclass
class StageSurface:
    width: ctypes.c_uint32 = 0
    height: ctypes.c_uint32 = 0
    dxgi_format: ctypes.c_uint32 = DXGI_FORMAT_B8G8R8A8_UNORM
    desc: D3D11_TEXTURE2D_DESC = D3D11_TEXTURE2D_DESC()
    texture: ctypes.POINTER(ID3D11Texture2D) = None
    output: InitVar[Output] = None
    device: InitVar[Device] = None

    def __post_init__(self, output, device) -> None:
        self.rebuild(output, device)

    def release(self):
        if self.texture is not None:
            self.width = 0
            self.height = 0
            self.texture.Release()
            self.texture = None

    def rebuild(self, output: Output, device: Device, dim: Tuple[int] = None):
        if dim is not None:
            self.width, self.height = dim
        else:
            self.width, self.height = output.surface_size

        if self.texture is None:
            self.desc.Width = self.width
            self.desc.Height = self.height
            self.desc.Format = self.dxgi_format
            self.desc.MipLevels = 1
            self.desc.ArraySize = 1
            self.desc.SampleDesc.Count = 1
            self.desc.SampleDesc.Quality = 0
            self.desc.Usage = D3D11_USAGE_STAGING
            self.desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ
            self.desc.MiscFlags = 0
            self.desc.BindFlags = 0
            self.texture = ctypes.POINTER(ID3D11Texture2D)()

            device.device.CreateTexture2D(
                ctypes.byref(self.desc),
                None,
                ctypes.byref(self.texture),
            )

            self.interface = self.texture.QueryInterface(IDXGISurface)

    def map(self):
        rect: DXGI_MAPPED_RECT = DXGI_MAPPED_RECT()
        self.interface.Map(ctypes.byref(rect), 1)
        return rect

    def unmap(self):
        self.interface.Unmap()

    def __repr__(self) -> str:
        repr = f"{self.width}, {self.height}, {self.dxgi_format}"
        return repr


class ProcessorBackends(enum.Enum):
    PIL = 0
    NUMPY = 1


class Processor:
    def __init__(self):
        self.cvtcolor = None
        self.PBYTE = ctypes.POINTER(ctypes.c_ubyte)

    def process(self, rect, width, height, region, rotation_angle):
        width = region[2] - region[0]
        height = region[3] - region[1]
        if rotation_angle in (90, 270):
            width, height = height, width

        buffer = ctypes.cast(rect.pBits, self.PBYTE)
        image = as_array(buffer, (height, width, 4))

        if rotation_angle != 0:
            image = rot90(image, k=rotation_angle // 90, axes=(1, 0))

        self.cvtcolor = lambda image: image[:, :, :3]
        return self.cvtcolor(image)


def enum_dxgi_adapters() -> List[ctypes.POINTER(IDXGIAdapter1)]:
    create_dxgi_factory = ctypes.windll.dxgi.CreateDXGIFactory1
    create_dxgi_factory.argtypes = (comtypes.GUID, ctypes.POINTER(ctypes.c_void_p))
    create_dxgi_factory.restype = ctypes.c_int32
    pfactory = ctypes.c_void_p(0)
    create_dxgi_factory(IDXGIFactory1._iid_, ctypes.byref(pfactory))
    dxgi_factory = ctypes.POINTER(IDXGIFactory1)(pfactory.value)
    i = 0
    p_adapters = list()
    while True:
        try:
            p_adapter = ctypes.POINTER(IDXGIAdapter1)()
            dxgi_factory.EnumAdapters1(i, ctypes.byref(p_adapter))
            p_adapters.append(p_adapter)
            i += 1
        except comtypes.COMError as ce:
            if ctypes.c_int32(DXGI_ERROR_NOT_FOUND).value == ce.args[0]:
                break
            else:
                raise ce
    return p_adapters


class DXCamera:
    def __init__(
            self,
            output,
            device,
            imgsize,
    ) -> None:
        self._output: Output = output
        self._device: Device = device
        self._imgsize = imgsize

        self._stagesurf: StageSurface = StageSurface(
            output=self._output, device=self._device
        )

        self._duplicator: Duplicator = Duplicator(
            output=self._output, device=self._device
        )

        self._processor: Processor = Processor()
        self._sourceRegion: D3D11_BOX = D3D11_BOX()
        self._sourceRegion.front = 0
        self._sourceRegion.back = 1

        self.width, self.height = self._output.resolution
        self.shot_w, self.shot_h = self.width, self.height
        self.rotation_angle: int = self._output.rotation_angle

        # 获取 user32.dll 的句柄
        user32 = ctypes.windll.user32

        # 获取主要显示器的分辨率
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        imgsize = int(self._imgsize)  # 只能用320
        fbl = [int(width), int(height)]

        szb = [int((fbl[0] / 2) - (imgsize / 2)), int((fbl[1] / 2) - (imgsize / 2))]
        xzb = [int((fbl[0] / 2) + (imgsize / 2)), int((fbl[1] / 2) + (imgsize / 2))]

        region = (0, 0, width, height)

        self._region_set_by_user = region is not None

        self.region: Tuple[int, int, int, int] = region
        self._validate_region(self.region)

        self.devices, self.outputs = [], []

        self.is_capturing = False

        self.__thread = None
        self.__lock = Lock()
        self.__stop_capture = Event()

        self.__frame_available = Event()
        self.__frame_buffer: np.ndarray = None
        self.__head = 0
        self.__tail = 0
        self.__full = False

        self.__timer_handle = None

        self.__frame_count = 0
        self.__capture_start_time = 0

        self.frame = None

        _region = self.region_to_memory_region(self.region, self.rotation_angle,
                                               self._output)
        _width = _region[2] - _region[0]
        _height = _region[3] - _region[1]

        if self._stagesurf.width != _width or self._stagesurf.height != _height:
            self._stagesurf.release()
            self._stagesurf.rebuild(output=self._output, device=self._device,
                                    dim=(_width, _height))

        self.texture = ctypes.POINTER(ID3D11Texture2D)()
        self._device.device.CreateTexture2D(
            ctypes.byref(self._stagesurf.desc),
            None,
            ctypes.byref(self.texture),
        )

        self.interface = self.texture.QueryInterface(IDXGISurface)

        self.rect = DXGI_MAPPED_RECT()
        self.interface.Map(ctypes.byref(self.rect), 1)
        self.interface.Unmap()

    def region_to_memory_region(self, region: Tuple[int, int, int, int], rotation_angle: int,
                                output: Output):
        if rotation_angle == 0:
            return region
        elif rotation_angle == 90:
            return (region[1], output.surface_size[1] - region[2], region[3],
                    output.surface_size[1] - region[0])
        elif rotation_angle == 180:
            return (output.surface_size[0] - region[2],
                    output.surface_size[1] - region[3],
                    output.surface_size[0] - region[0],
                    output.surface_size[1] - region[1])
        else:
            return (output.surface_size[0] - region[3], region[0],
                    output.surface_size[0] - region[1], region[2])

    def grab(self):
        try:
            if self._duplicator.update_frame():
                if not self._duplicator.updated:
                    self.frame = np.array(self.frame)
                    return self.frame

                self._device.im_context.CopySubresourceRegion(
                    self.texture, 0, 0, 0, 0, self._duplicator.texture, 0,
                    ctypes.byref(self._sourceRegion)
                )
                self._duplicator.release_frame()

                self.frame = self._processor.process(
                    self.rect, self.shot_w, self.shot_h, self.region, self.rotation_angle
                )

                return np.array(self.frame)
        except:
            self.reset_device()
            return np.array(self.frame)

    def _validate_region(self, region: Tuple[int, int, int, int]):
        l, t, r, b = region
        if not (self.width >= r > l >= 0 and self.height >= b > t >= 0):
            raise ValueError(
                f"Invalid Region: Region should be in {self.width}x{self.height}"
            )
        self.region = region
        self._sourceRegion.left = region[0]
        self._sourceRegion.top = region[1]
        self._sourceRegion.right = region[2]
        self._sourceRegion.bottom = region[3]
        self.shot_w, self.shot_h = region[2] - region[0], region[3] - region[1]

    def reset_device(self):
        p_adapters = enum_dxgi_adapters()
        self.devices, self.outputs = [], []
        for p_adapter in p_adapters:
            device = Device(p_adapter)
            p_outputs = device.enum_outputs()
            if len(p_outputs) != 0:
                self.devices.append(device)
                self.outputs.append([Output(p_output) for p_output in p_outputs])

        device = self.devices[0]
        output = self.outputs[0][0]
        output.update_desc()

        self._output: Output = output
        self._device: Device = device

        _region = self.region_to_memory_region(self.region, self.rotation_angle,
                                               self._output)
        _width = _region[2] - _region[0]
        _height = _region[3] - _region[1]

        if self._stagesurf.width != _width or self._stagesurf.height != _height:
            self._stagesurf.release()
            self._stagesurf.rebuild(output=self._output, device=self._device,
                                    dim=(_width, _height))

        self.texture = ctypes.POINTER(ID3D11Texture2D)()
        self._device.device.CreateTexture2D(
            ctypes.byref(self._stagesurf.desc),
            None,
            ctypes.byref(self.texture),
        )

        self.interface = self.texture.QueryInterface(IDXGISurface)

        self.rect = DXGI_MAPPED_RECT()
        self.interface.Map(ctypes.byref(self.rect), 1)
        self.interface.Unmap()

        self._duplicator: Duplicator = Duplicator(
            output=self._output, device=self._device
        )

        self.width, self.height = self._output.resolution
        self.shot_w, self.shot_h = self.width, self.height
        self.rotation_angle: int = self._output.rotation_angle

        # 获取 user32.dll 的句柄
        user32 = ctypes.windll.user32

        # 获取主要显示器的分辨率
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)

        imgsize = int(self._imgsize)  # 只能用320
        fbl = [int(width), int(height)]

        szb = [int((fbl[0] / 2) - (imgsize / 2)), int((fbl[1] / 2) - (imgsize / 2))]
        xzb = [int((fbl[0] / 2) + (imgsize / 2)), int((fbl[1] / 2) + (imgsize / 2))]

        region = (szb[0], szb[1], xzb[0], xzb[1])

        self._region_set_by_user = region is not None

        self.region: Tuple[int, int, int, int] = region
        if self.region is None:
            self.region = (0, 0, self.width, self.height)
        self._validate_region(self.region)


def DXcreate(imgsize):
    # win32api.MessageBox(0, f"DX截图模块调用成功，模块免费，如被收费我只能对你哈哈大笑", "DX截图", win32con.MB_OK)
    p_adapters = enum_dxgi_adapters()
    devices, outputs = [], []
    for p_adapter in p_adapters:
        device = Device(p_adapter)
        p_outputs = device.enum_outputs()
        if len(p_outputs) != 0:
            devices.append(device)
            outputs.append([Output(p_output) for p_output in p_outputs])

    device = devices[0]
    output = outputs[0][0]
    output.update_desc()

    camera = DXCamera(
        output=output,
        device=device,
        imgsize=imgsize,
    )
    return camera


Cp = DXcreate(320)  # 截图尺寸
# import time, cv2
#
# while True:
#     t0 = time.perf_counter()
#     img = Cp.grab()
#     t1 = time.perf_counter() - t0
#     t2 = time.perf_counter()
#     cv2.putText(img, f'ms: {(t1 * 1000):.2f}', (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 1,
#                 (255, 0, 0), 2)
#     cv2.imshow('1', img)
#     cv2.waitKey(1)
#     print(f'截图耗时(ms): {(t1 * 1000):.5f}, OpenCv耗时(ms): {((time.perf_counter() - t2) * 1000):.5f}')

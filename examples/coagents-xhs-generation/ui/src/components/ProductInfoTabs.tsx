"use client";

import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Download, FileText, AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";
import { ProductInfo, BriefData } from "@/lib/types";

interface ProductInfoTabsProps {
  productInfo: ProductInfo;
  briefData: BriefData | null;
  onProductInfoUpdate: (productInfo: ProductInfo) => void;
  onBriefDataUpdate: (briefData: BriefData | null) => void;
}

export function ProductInfoTabs({ 
  productInfo, 
  briefData, 
  onProductInfoUpdate, 
  onBriefDataUpdate 
}: ProductInfoTabsProps) {
  
  const [activeTab, setActiveTab] = useState("manual");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [dragActive, setDragActive] = useState(false);

  // 处理产品信息字段更新
  const handleFieldUpdate = (field: keyof ProductInfo, value: string | string[]) => {
    onProductInfoUpdate({
      ...productInfo,
      [field]: value,
    });
  };

  // 下载模板
  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/brief/parse');
      const result = await response.json();
      
      if (result.success) {
        const link = document.createElement('a');
        link.href = result.templateUrl;
        link.download = '晴月文化传媒xx品牌KOC达人brief表.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error) {
      console.error('模板下载失败:', error);
      setErrorMessage('模板下载失败，请重试');
      setUploadStatus('error');
    }
  };

  // 确保briefData始终有值以便编辑
  const ensureBriefData = () => {
    if (!briefData) {
      const emptyBriefData = {
        brandName: '',
        productName: '',
        productPrice: '',
        productFunction: '',
        usageMethod: '',
        storeLink: '',
        targetAudience: '',
        usageScenario: '',
        coreSellingPoint1: '',
        coreSellingPoint2: '',
        coreSellingPoint3: '',
        auxiliarySellingPoints: '',
        painPointType: '',
        budgetRange: '',
        isSupplyScript: '',
        isCarLink: '',
        isFreeShipping: '',
        isReporting: '',
        expectedPublishTime: '',
        collaboratorCount: '',
        fansCount: '',
        contentCategory: '',
        bloggerGender: '',
        bloggerAge: '',
        promotionChannels: '',
        imageTextTitle: '',
        imageTextPoints: '',
        imageCount: '',
        productImageRatio: '',
        textWordCount: '',
        videoLength: '',
        videoPoints: '',
        videoDetailDisplay: '',
        contentStyle: '',
        hasSubtitles: '',
        bgmRequirements: '',
        realPersonAppearance: '',
        topicStyles: '',
        mustIncludeKeywords: '',
        mustIncludeTopics: '',
        mustIncludeTags: '',
        excellentCaseReference: '',
        deadlineConfirmation: '',
        scriptProvided: '',
        scriptAuditRequired: '',
        contentRetentionPeriod: '',
        materialAuthorizationRights: '',
        brandPinToTop: '',
        commentGuidance: '',
        trafficMaintenance: '',
        contentBoost: '',
        otherRequirements: '',
        uploadTime: new Date().toISOString()
      };
      return emptyBriefData;
    }
    return briefData;
  };

  // 处理文件上传
  const handleFileUpload = async (file: File) => {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
      setErrorMessage('请上传 Excel 文件 (.xlsx 或 .xls)');
      setUploadStatus('error');
      return;
    }

    setIsUploading(true);
    setUploadStatus('idle');
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/brief/parse', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();

      if (result.success) {
        const briefData = result.data;
        
        // 首先更新Brief数据
        onBriefDataUpdate(briefData);
        
        // 从Brief表数据中提取特点和卖点
        const extractedFeatures = [];
        if (briefData.productFunction) extractedFeatures.push(briefData.productFunction);
        if (briefData.usageMethod) extractedFeatures.push(briefData.usageMethod);
        
        const extractedSellingPoints = [];
        if (briefData.coreSellingPoint1) extractedSellingPoints.push(briefData.coreSellingPoint1);
        if (briefData.coreSellingPoint2) extractedSellingPoints.push(briefData.coreSellingPoint2);
        if (briefData.coreSellingPoint3) extractedSellingPoints.push(briefData.coreSellingPoint3);
        if (briefData.auxiliarySellingPoints) extractedSellingPoints.push(briefData.auxiliarySellingPoints);

        // 同时更新产品信息
        onProductInfoUpdate({
          ...productInfo,
          name: briefData.productName || productInfo.name,
          category: briefData.painPointType || productInfo.category,
          target_audience: briefData.targetAudience || productInfo.target_audience,
          features: extractedFeatures.length > 0 ? extractedFeatures : productInfo.features,
          selling_points: extractedSellingPoints.length > 0 ? extractedSellingPoints : productInfo.selling_points,
        });
        
        setUploadStatus('success');
        
        // 2秒后自动切换到手动输入选项卡
        setTimeout(() => {
          setActiveTab("manual");
        }, 2000);
      } else {
        setErrorMessage(result.error || '文件解析失败');
        setUploadStatus('error');
      }
    } catch (error) {
      setErrorMessage(`文件上传失败: ${error instanceof Error ? error.message : '未知错误'}`);
      setUploadStatus('error');
    } finally {
      setIsUploading(false);
    }
  };

  // 拖拽处理
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  // 文件选择处理
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  // 重新上传Brief表
  const handleReupload = () => {
    setActiveTab("brief");
    onBriefDataUpdate(null);
    setUploadStatus('idle');
    setErrorMessage('');
  };

  
  return (
    <div>
      <h2 className="text-lg font-medium mb-3 text-primary">产品信息</h2>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="manual">手动输入</TabsTrigger>
          <TabsTrigger value="brief">Brief表上传</TabsTrigger>
        </TabsList>

        <TabsContent value="manual" className="space-y-6 bg-background p-6 rounded-xl">
          {/* 数据来源提示 */}
          {briefData && (
            <div className="flex items-center justify-between mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg shadow-sm">
              <div className="flex items-center">
                <CheckCircle2 className="w-5 h-5 text-blue-600 mr-3" />
                <div>
                  <div className="text-sm font-medium text-blue-900">数据来源：Brief表</div>
                  <div className="text-xs text-blue-700">上传于 {new Date(briefData.uploadTime).toLocaleString('zh-CN')}</div>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleReupload}
                className="text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
              >
                <RefreshCw className="w-3 h-3 mr-1" />
                重新上传
              </Button>
            </div>
          )}

          {/* 核心产品信息 - 仅显示与文案创作相关的8个字段 */}
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">品牌名称</label>
                <Input
                  placeholder="请输入品牌名称"
                  value={briefData?.brandName || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      brandName: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Brand name"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">产品名称</label>
                <Input
                  placeholder="请输入产品名称"
                  value={briefData?.productName || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      productName: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Product name"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">售价</label>
                <Input
                  placeholder="请输入产品售价"
                  value={briefData?.productPrice || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      productPrice: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Product price"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">功效</label>
                <Input
                  placeholder="请输入产品功效"
                  value={briefData?.productFunction || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      productFunction: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Product function"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">使用方法</label>
                <Input
                  placeholder="请输入使用方法"
                  value={briefData?.usageMethod || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      usageMethod: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Usage method"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">目标受众</label>
                <Input
                  placeholder="请输入目标受众"
                  value={briefData?.targetAudience || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      targetAudience: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Target audience"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">使用场景</label>
                <Input
                  placeholder="请输入使用场景"
                  value={briefData?.usageScenario || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      usageScenario: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Usage scenario"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">产品痛点切入</label>
                <Input
                  placeholder="请输入产品痛点切入"
                  value={briefData?.painPointType || ""}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    onBriefDataUpdate({
                      ...currentBrief,
                      painPointType: e.target.value,
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Pain point type"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors"
                />
              </div>
            </div>

            {/* 合并的产品卖点字段 */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">产品卖点</label>
              <div className="relative">
                <Input
                  placeholder="请输入产品卖点，多个卖点请用逗号分隔"
                  value={briefData ? [briefData.coreSellingPoint1, briefData.coreSellingPoint2, briefData.coreSellingPoint3, briefData.auxiliarySellingPoints].filter(Boolean).join(', ') : ''}
                  onChange={(e) => {
                    const currentBrief = ensureBriefData();
                    const sellingPoints = e.target.value ? e.target.value.split(',').map(s => s.trim()).filter(s => s) : [];
                    
                    onBriefDataUpdate({
                      ...currentBrief,
                      coreSellingPoint1: sellingPoints[0] || '',
                      coreSellingPoint2: sellingPoints[1] || '',
                      coreSellingPoint3: sellingPoints[2] || '',
                      auxiliarySellingPoints: sellingPoints.slice(3).join(', ') || '',
                      uploadTime: currentBrief.uploadTime || new Date().toISOString()
                    });
                  }}
                  aria-label="Product selling points"
                  className="border border-gray-200 shadow-sm text-sm focus:border-blue-400 focus:ring-2 focus:ring-blue-100 placeholder:text-gray-400 transition-colors pr-10"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
                  用逗号分隔
                </div>
              </div>
            </div>
          </div>


        </TabsContent>

        <TabsContent value="brief" className="space-y-6">
          <div className="bg-background p-8 rounded-xl border border-gray-100 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-1">上传Brief表</h3>
                <p className="text-sm text-gray-600">快速填充产品信息，提高创作效率</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownloadTemplate}
                className="text-sm font-medium border-blue-200 text-blue-700 hover:bg-blue-50 hover:border-blue-300"
              >
                <Download className="w-4 h-4 mr-2" />
                下载模板
              </Button>
            </div>

            {/* 上传区域 */}
            <div
              className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-200 ${
                dragActive 
                  ? 'border-blue-400 bg-gradient-to-b from-blue-50 to-blue-100 shadow-md' 
                  : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                dragActive ? 'bg-blue-200' : 'bg-gray-100'
              }`}>
                <Upload className={`h-8 w-8 ${dragActive ? 'text-blue-600' : 'text-gray-500'}`} />
              </div>
              <div className="text-lg font-semibold text-gray-800 mb-2">
                上传Brief表文件
              </div>
              <div className="text-sm text-gray-600 mb-6">
                拖拽文件到此处，或点击下方按钮选择文件
              </div>
              
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileSelect}
                className="hidden"
                id="brief-file-input"
                disabled={isUploading}
              />
              
              <Button
                variant="default"
                onClick={() => {
                  const fileInput = document.getElementById('brief-file-input');
                  fileInput?.click();
                }}
                disabled={isUploading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 mb-4 shadow-sm"
              >
                <FileText className="w-4 h-4 mr-2" />
                {isUploading ? '上传中...' : '选择文件'}
              </Button>

              <div className="text-xs text-gray-500 bg-gray-50 px-3 py-1 rounded-full inline-block">
                支持 .xlsx 和 .xls 格式
              </div>
            </div>

            {/* 状态提示 */}
            {uploadStatus === 'success' && (
              <div className="flex items-center mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg shadow-sm">
                <CheckCircle2 className="w-5 h-5 text-green-600 mr-3" />
                <div>
                  <div className="text-sm font-medium text-green-900">Brief表解析成功！</div>
                  <div className="text-xs text-green-700">即将切换到手动输入选项卡...</div>
                </div>
              </div>
            )}

            {uploadStatus === 'error' && errorMessage && (
              <div className="flex items-start mt-6 p-4 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-lg shadow-sm">
                <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
                <div className="text-sm text-red-800">
                  <div className="font-medium mb-1">上传失败</div>
                  <div className="text-red-700">{errorMessage}</div>
                </div>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
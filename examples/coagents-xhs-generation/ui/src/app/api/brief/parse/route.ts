import { NextRequest, NextResponse } from 'next/server';
import * as XLSX from 'xlsx';
import { BriefData } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json({ error: '请选择要上传的文件' }, { status: 400 });
    }

    // 验证文件类型
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
      return NextResponse.json({ error: '请上传 Excel 文件 (.xlsx 或 .xls)' }, { status: 400 });
    }

    // 读取文件内容
    const arrayBuffer = await file.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    
    // 获取第一个工作表
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    
    // 将工作表转换为JSON
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
    
    // 解析 Brief 表数据
    const briefData: BriefData = parseBriefData(jsonData as any[][]);
    
    console.log('API返回的briefData:', JSON.stringify(briefData, null, 2));
    
    return NextResponse.json({ 
      success: true, 
      data: briefData,
      message: 'Brief 表解析成功'
    });

  } catch (error) {
    console.error('Brief 表解析错误:', error);
    return NextResponse.json({ 
      error: '文件解析失败，请检查文件格式是否正确',
      details: error instanceof Error ? error.message : '未知错误'
    }, { status: 500 });
  }
}

function parseBriefData(data: any[][]): BriefData {
  console.log('开始解析Brief表数据:', data.length, '行');
  
  // 创建一个更精确的映射来查找数据
  const findValueByExactMatch = (searchTerms: string[]): string => {
    for (let rowIndex = 0; rowIndex < data.length; rowIndex++) {
      const row = data[rowIndex];
      for (let colIndex = 0; colIndex < row.length - 1; colIndex++) {
        const cell = String(row[colIndex] || '').trim();
        
        // 精确匹配字段名
        if (searchTerms.includes(cell)) {
          // 查找同行右侧的值，或者下一行对应位置的值
          let value = String(row[colIndex + 1] || '').trim();
          
          // 如果同行右侧没有值，尝试查找下一行相同位置的值
          if (!value && rowIndex + 1 < data.length) {
            value = String(data[rowIndex + 1][colIndex] || '').trim();
          }
          
          // 清理placeholder文本
          if (value && !isPlaceholderText(value)) {
            console.log(`找到字段 "${cell}": "${value}"`);
            return value;
          }
        }
      }
    }
    return '';
  };

  // 检查是否是placeholder文本
  const isPlaceholderText = (text: string): boolean => {
    const cleaned = text.toLowerCase().trim();
    return cleaned === '' || 
           /^x+$/.test(cleaned) || 
           cleaned.includes('待填') ||
           cleaned.includes('请填') ||
           cleaned === '是/否' ||
           cleaned === '免费/不免费' ||
           /^\(.+\)$/.test(cleaned); // 括号内的提示文本
  };

  // 根据分类和字段名查找值
  const findValueInSection = (sectionKeywords: string[], fieldKeywords: string[]): string => {
    // 首先找到包含分类关键词的行
    let sectionStartRow = -1;
    let sectionEndRow = data.length;
    
    for (let i = 0; i < data.length; i++) {
      const rowText = data[i].join(' ').toLowerCase();
      if (sectionKeywords.some(keyword => rowText.includes(keyword.toLowerCase()))) {
        sectionStartRow = i;
        break;
      }
    }

    // 找到下一个分类的开始行作为结束行
    if (sectionStartRow >= 0) {
      for (let i = sectionStartRow + 1; i < data.length; i++) {
        const cell = String(data[i][0] || '').trim();
        // 如果是新的分类标题，则结束当前分类
        if (cell && cell.length > 0 && 
            ['品牌介绍', '产品介绍', '产品卖点', '产品痛点切入', '合作需求', '博主要求', '内容形式', '内容风格', '发布要求', '激励政策'].includes(cell)) {
          sectionEndRow = i;
          break;
        }
      }
    }

    // 在指定分类范围内查找字段
    if (sectionStartRow >= 0) {
      for (let rowIndex = sectionStartRow; rowIndex < sectionEndRow; rowIndex++) {
        const row = data[rowIndex];
        for (let colIndex = 0; colIndex < row.length - 1; colIndex++) {
          const cell = String(row[colIndex] || '').trim();
          
          if (fieldKeywords.includes(cell)) {
            let value = String(row[colIndex + 1] || '').trim();
            
            if (!value && rowIndex + 1 < data.length) {
              value = String(data[rowIndex + 1][colIndex] || '').trim();
            }
            
            if (value && !isPlaceholderText(value)) {
              console.log(`在分类中找到字段 "${cell}": "${value}"`);
              return value;
            }
          }
        }
      }
    }

    // 智能回退：只有当字段名不是常见的通用词时才进行全局查找
    const isGenericFieldName = ['类型', '名称', '数量', '时间', '要求'].some(generic => 
      fieldKeywords.some(field => field.includes(generic))
    );
    
    if (!isGenericFieldName) {
      // 对于非通用字段名，可以安全地进行全局查找
      console.log(`字段 [${fieldKeywords.join(', ')}] 非通用名称，尝试全局查找`);
      return findValueByExactMatch(fieldKeywords);
    } else {
      // 对于通用字段名，避免跨分区匹配
      console.log(`在分类 [${sectionKeywords.join(', ')}] 中未找到通用字段 [${fieldKeywords.join(', ')}]，避免全局查找`);
      return '';
    }
  };

  // 解析Brief表数据，确保所有字段都有默认值
  const result = {
    // 基本信息
    brandName: findValueInSection(['品牌介绍'], ['品牌名称', '品牌']) || '',
    productName: findValueInSection(['品牌介绍'], ['产品名称']) || '',
    productPrice: findValueInSection(['品牌介绍'], ['售价']) || '',
    productFunction: findValueInSection(['品牌介绍'], ['功效']) || '',
    usageMethod: findValueInSection(['品牌介绍'], ['使用方法']) || '',
    storeLink: findValueInSection(['品牌介绍'], ['店铺/链接', '链接']) || '',
    
    // 产品介绍
    targetAudience: findValueInSection(['产品介绍'], ['目标受众']) || '',
    usageScenario: findValueInSection(['产品介绍'], ['使用场景']) || '',
    coreSellingPoint1: findValueInSection(['产品介绍', '产品卖点'], ['核心卖点1']) || '',
    coreSellingPoint2: findValueInSection(['产品介绍', '产品卖点'], ['核心卖点2']) || '',
    coreSellingPoint3: findValueInSection(['产品介绍', '产品卖点'], ['核心卖点3']) || '',
    auxiliarySellingPoints: findValueInSection(['产品介绍', '产品卖点'], ['辅助卖点']) || '',
    
    // 产品痛点切入
    painPointType: findValueInSection(['产品痛点切入'], ['类型', '痛点类型', '切入点']) || '',
    budgetRange: findValueInSection(['产品痛点切入'], ['单条预算范围', '预算范围']) || '',
    
    // 合作需求
    isSupplyScript: findValueInSection(['合作需求'], ['是否供稿']) || '',
    isCarLink: findValueInSection(['合作需求'], ['是否挂车']) || '',
    isFreeShipping: findValueInSection(['合作需求'], ['是否免费寄样']) || '',
    isReporting: findValueInSection(['合作需求'], ['是否报备']) || '',
    expectedPublishTime: findValueInSection(['合作需求'], ['预期发布时间']) || '',
    
    // 博主要求
    collaboratorCount: findValueInSection(['博主要求'], ['人数']) || '',
    fansCount: findValueInSection(['博主要求'], ['粉丝数目']) || '',
    contentCategory: findValueInSection(['博主要求'], ['内容类目']) || '',
    bloggerGender: findValueInSection(['博主要求'], ['博主性别']) || '',
    bloggerAge: findValueInSection(['博主要求'], ['博主年龄']) || '',
    promotionChannels: findValueInSection(['博主要求'], ['推广渠道']) || '',
    
    // 内容形式 - 图文
    imageTextTitle: findValueInSection(['内容形式'], ['标题必须', '标题要求']) || '',
    imageTextPoints: findValueInSection(['内容形式'], ['必须要点', '可提要点']) || '',
    imageCount: findValueInSection(['内容形式'], ['图片不少于', '图片数量']) || '',
    productImageRatio: findValueInSection(['内容形式'], ['产品图片不少于', '产品图片比例']) || '',
    textWordCount: findValueInSection(['内容形式'], ['文案不少于', '文案字数']) || '',
    
    // 内容形式 - 视频
    videoLength: findValueInSection(['内容形式'], ['视频时长']) || '',
    videoPoints: findValueInSection(['内容形式'], ['必提要点']) || '',
    videoDetailDisplay: findValueInSection(['内容形式'], ['产品细节展示']) || '',
    
    // 内容风格和要求
    contentStyle: findValueInSection(['内容风格', '约定风险管制'], ['风格', '内容风格']) || '',
    hasSubtitles: findValueInSection(['约定风险管制'], ['是否带有字幕']) || '',
    bgmRequirements: findValueInSection(['约定风险管制'], ['BGM要求']) || '',
    realPersonAppearance: findValueInSection(['约定风险管制'], ['是否真人出镜']) || '',
    
    // 选题和关键词
    topicStyles: findValueInSection(['选题风格'], ['选题风格', '选题1', '选题2', '选题3']) || '',
    mustIncludeKeywords: findValueInSection(['必带关键词'], ['必带关键词']) || '',
    mustIncludeTopics: findValueInSection(['必带话题'], ['必带话题']) || '',
    mustIncludeTags: findValueInSection(['必带标签'], ['必带标签']) || '',
    
    // 参考和审核
    excellentCaseReference: findValueInSection(['优秀案例参考'], ['优秀案例参考']) || '',
    deadlineConfirmation: findValueInSection(['离期确认'], ['离期确认']) || '',
    scriptProvided: findValueInSection(['脚本/素材是否提供'], ['脚本/素材是否提供']) || '',
    scriptAuditRequired: findValueInSection(['脚本/素材是否审核'], ['脚本/素材是否审核']) || '',
    
    // 发布要求
    contentRetentionPeriod: findValueInSection(['发布要求'], ['内容保留']) || '',
    materialAuthorizationRights: findValueInSection(['发布要求'], ['素材授权']) || '',
    brandPinToTop: findValueInSection(['发布要求'], ['品牌置顶']) || '',
    
    // 评论区引导与维护
    commentGuidance: findValueInSection(['评论区引导与维护'], ['评论区引导与维护']) || '',
    
    // 激励政策
    trafficMaintenance: findValueInSection(['激励政策'], ['流量维护']) || '',
    contentBoost: findValueInSection(['激励政策'], ['内容加热']) || '',
    
    // 其他
    otherRequirements: findValueInSection(['其他事项'], ['其他事项']) || '',
    uploadTime: new Date().toISOString(),
  };

  // 确保所有字段都有默认空字符串值
  Object.keys(result).forEach(key => {
    if (key !== 'uploadTime' && (result[key as keyof typeof result] === undefined || result[key as keyof typeof result] === null)) {
      (result as any)[key] = '';
    }
  });

  console.log('Brief表解析完成，字段数量:', Object.keys(result).length);
  return result;
}

// 提供模板下载功能
export async function GET() {
  try {
    const templatePath = '/templates/晴月文化传媒xx品牌KOC达人brief表.xlsx';
    
    return NextResponse.json({
      success: true,
      templateUrl: templatePath,
      message: '模板下载链接获取成功'
    });
  } catch (error) {
    return NextResponse.json(
      { error: '模板下载失败' },
      { status: 500 }
    );
  }
}
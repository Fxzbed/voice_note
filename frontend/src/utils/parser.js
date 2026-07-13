/**
 * 解析 JSON 数据（支持三种格式）
 * @param {string} jsonString - JSON 字符串
 * @returns {Array} 笔记数组
 */
export function parseNotesJSON(jsonString) {
  try {
    const data = JSON.parse(jsonString)
    
    // 格式 1: 直接数组格式
    if (Array.isArray(data)) {
      return data
    }
    
    // 格式 2: 包含 notes 数组字段的对象
    if (data.notes && Array.isArray(data.notes)) {
      return data.notes
    }
    
    // 格式 3: 包含 data 数组字段的对象
    if (data.data && Array.isArray(data.data)) {
      return data.data
    }
    
    throw new Error('无法识别的 JSON 格式，请确保数据包含 notes、data 字段或直接为数组')
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error('JSON 格式错误: ' + error.message)
    }
    throw error
  }
}

/**
 * 验证笔记数据格式
 * @param {Array} notes - 笔记数组
 * @returns {Array} 验证后的笔记数组
 */
export function validateNotes(notes) {
  if (!Array.isArray(notes)) {
    throw new Error('数据必须是数组格式')
  }
  
  return notes.map((note, index) => {
    if (typeof note !== 'object' || note === null) {
      throw new Error(`第 ${index + 1} 条笔记格式错误`)
    }
    
    const summary = note.summary || ''
    const knowledge_points = Array.isArray(note.knowledge_points) 
      ? note.knowledge_points 
      : []
    
    return { 
      summary, 
      knowledge_points,
      id: `note-${index}`
    }
  })
}

/**
 * 计算统计数据
 * @param {Array} notes - 笔记数组
 * @returns {Object} 统计信息
 */
export function calculateStats(notes) {
  const totalNotes = notes.length
  const totalKPs = notes.reduce((sum, note) => sum + note.knowledge_points.length, 0)
  const avgKPs = totalNotes > 0 ? (totalKPs / totalNotes).toFixed(1) : '0'
  
  return {
    totalNotes,
    totalKPs,
    avgKPs
  }
}

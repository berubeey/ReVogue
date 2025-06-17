'use client'

import { useState } from 'react'

interface HistoryItem {
  text: string
  context: {
    location: string
    event: string
    calendar_summary: string
    weather: {
      temperature: number
      condition: string
      humidity: number
      wind_speed: number
      precipitation: number
      uv_index: number
      sunrise: string
      sunset: string
    }
    timestamp: string
  }
  outfit_advice: string
}

const API_BASE_URL = 'http://localhost:8004'

async function fetchWithRetry(url: string, options: RequestInit, retries = 3): Promise<Response> {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }
      return response
    } catch (error) {
      if (i === retries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))) // Exponential backoff
    }
  }
  throw new Error('Failed to fetch after retries')
}

export default function Home() {
  const [text, setText] = useState('')
  const [profession, setProfession] = useState('')
  const [personality, setPersonality] = useState('')
  const [response, setResponse] = useState<HistoryItem | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // 從文本中提取地點和事件類型
      const locationMatch = text.match(/在(.*?)(?:開會|見面|參加|舉辦)/)
      const eventMatch = text.match(/(?:開會|見面|參加|舉辦)(.*?)(?:，|。|$)/)
      
      const location = locationMatch?.[1] || '台北'
      const eventType = eventMatch?.[1] || '一般活動'

      const response = await fetchWithRetry(
        `${API_BASE_URL}/api/analyze-image`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: text,
            user_data: {
              location,
              event_type: eventType,
              profession,
              personality,
            }
          }),
        }
      )

      const data = await response.json()
      
      const newResponse = {
        text,
        context: {
          location,
          event: eventType,
          calendar_summary: '',
          weather: data.weather || {},
          timestamp: new Date().toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' }),
        },
        outfit_advice: data.advice,
      }
      
      setResponse(newResponse)
      setHistory((prev) => [newResponse, ...prev])
      setText('')
    } catch (err) {
      console.error('Error:', err)
      setError(err instanceof Error ? err.message : '無法連接到伺服器，請確認後端服務是否正在運行')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">AI 形象顧問</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg shadow-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              您的需求
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full p-2 border rounded-md"
              rows={4}
              placeholder="請描述您的需求，例如：'我明天要去台北信義區開會，需要穿得正式一點...'"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              您的職業
            </label>
            <input
              type="text"
              value={profession}
              onChange={(e) => setProfession(e.target.value)}
              className="w-full p-2 border rounded-md"
              placeholder="例如：軟體工程師"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              您的性格
            </label>
            <input
              type="text"
              value={personality}
              onChange={(e) => setPersonality(e.target.value)}
              className="w-full p-2 border rounded-md"
              placeholder="例如：活潑外向"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
          >
            {isLoading ? '處理中...' : '獲取建議'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
            <p className="font-medium">錯誤：</p>
            <p>{error}</p>
            <p className="mt-2 text-sm">
              請確認：
              <ul className="list-disc list-inside mt-1">
                <li>後端服務器是否正在運行（python image_consultant_api.py）</li>
                <li>API 金鑰是否已正確設置在 .env 文件中</li>
                <li>網路連接是否正常</li>
              </ul>
            </p>
          </div>
        )}

        {isLoading && (
          <div className="mt-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">正在處理您的請求...</p>
          </div>
        )}

        {response && !isLoading && (
          <div className="mt-8 space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">情境分析</h2>
              <div className="space-y-2">
                <p><span className="font-medium">地點：</span>{response.context.location}</p>
                <p><span className="font-medium">場合：</span>{response.context.event}</p>
                <div className="mt-4">
                  <h3 className="font-medium mb-2">天氣資訊：</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <p><span className="font-medium">溫度：</span>{response.context.weather.temperature}°C</p>
                    <p><span className="font-medium">天氣：</span>{response.context.weather.condition}</p>
                    <p><span className="font-medium">濕度：</span>{response.context.weather.humidity}%</p>
                    <p><span className="font-medium">風速：</span>{response.context.weather.wind_speed} km/h</p>
                    <p><span className="font-medium">降雨量：</span>{response.context.weather.precipitation} mm</p>
                    <p><span className="font-medium">紫外線指數：</span>{response.context.weather.uv_index}</p>
                    <p><span className="font-medium">日出時間：</span>{response.context.weather.sunrise}</p>
                    <p><span className="font-medium">日落時間：</span>{response.context.weather.sunset}</p>
                  </div>
                </div>
                <p><span className="font-medium">時間：</span>{response.context.timestamp}</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-semibold mb-4">穿搭建議</h2>
              <div className="prose max-w-none">
                {response.outfit_advice.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {history.length > 0 && !isLoading && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">歷史記錄</h2>
            <div className="space-y-4">
              {history.map((item, index) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow-md">
                  <p className="text-gray-600 mb-2">{item.text}</p>
                  <div className="space-y-2">
                    <p><span className="font-medium">地點：</span>{item.context.location}</p>
                    <p><span className="font-medium">場合：</span>{item.context.event}</p>
                    <div className="mt-4">
                      <h3 className="font-medium mb-2">天氣資訊：</h3>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <p><span className="font-medium">溫度：</span>{item.context.weather.temperature}°C</p>
                        <p><span className="font-medium">天氣：</span>{item.context.weather.condition}</p>
                        <p><span className="font-medium">濕度：</span>{item.context.weather.humidity}%</p>
                        <p><span className="font-medium">風速：</span>{item.context.weather.wind_speed} km/h</p>
                        <p><span className="font-medium">降雨量：</span>{item.context.weather.precipitation} mm</p>
                        <p><span className="font-medium">紫外線指數：</span>{item.context.weather.uv_index}</p>
                        <p><span className="font-medium">日出時間：</span>{item.context.weather.sunrise}</p>
                        <p><span className="font-medium">日落時間：</span>{item.context.weather.sunset}</p>
                      </div>
                    </div>
                    <p><span className="font-medium">時間：</span>{item.context.timestamp}</p>
                  </div>
                  <div className="mt-4 prose max-w-none">
                    {item.outfit_advice.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

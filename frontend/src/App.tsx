import "./App.css"

import { Search, User, Bell, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState, useRef } from "react"

const timeSlots = ["8", "9", "10", "11", "12", "1", "2", "3", "4", "5", "6"]
const days = ["MON", "TUE", "WED", "THU", "FRI"]

type CellState = {
  preference: "default" | "preferred" | "unavailable"
  rank: number
  course_code?: string
}

type APIResponse = {
  course_code: string
  preferences?: string
  rank?: number
}

const defaultCellState: CellState = {
  preference: "default",
  rank: 3,
}

export default function TimetablePage() {
  const initializeTimetable = (): CellState[][] => {
    return timeSlots.map(() => days.map(() => ({ ...defaultCellState })))
  }

  const [activeTab, setActiveTab] = useState<"preferences" | "recommendations">("preferences")
  const [preferencesGrid, setPreferencesGrid] = useState<CellState[][]>(initializeTimetable())
  const [recommendationsGrid, setRecommendationsGrid] = useState<CellState[][]>(initializeTimetable())

  const [isDragging, setIsDragging] = useState(false)
  const [dragType, setDragType] = useState<"preferred" | "unavailable" | null>(null)
  const [dragStartPosition, setDragStartPosition] = useState<{ timeIndex: number; dayIndex: number } | null>(null)
  const [currentRank, setCurrentRank] = useState(1)
  const mouseDownTimeRef = useRef<number>(0)

  const [courseCode, setCourseCode] = useState("")
  const [courses, setCourses] = useState<string[]>([])
  const [semester, setSemester] = useState("S1")
  const [location, setLocation] = useState("STLUC")
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)

  const getCurrentGrid = () => {
    return activeTab === "preferences" ? preferencesGrid : recommendationsGrid
  }

  const capitalizeCourse = (code: string): string => {
    return code.toUpperCase()
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCourseCode(capitalizeCourse(event.target.value))
  }

  const convertTimetableForAPI = () => {
    const preferences: Record<string, { preference: string; rank: number }> = {}

    preferencesGrid.forEach((timeRow, timeIndex) => {
      timeRow.forEach((cell, dayIndex) => {
        if (cell.preference !== "default") {
          const cellKey = `${days[dayIndex]}-${timeSlots[timeIndex]}`
          preferences[cellKey] = {
            preference: cell.preference,
            rank: cell.rank,
          }
        }
      })
    })

    return preferences
  }

  const recommendTimetable = async () => {
    setIsLoadingRecommendations(true)
    try {
      const response = await fetch("http://127.0.0.1:5000/timetable", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          semester,
          location,
          courses,
          timetablePreferences: convertTimetableForAPI(),
        }),
      })

      if (response.ok) {
        const data = await response.json()
        handleGridResponse(data)
        setActiveTab("recommendations")
      }
    } catch (error) {
      console.error("Failed to load recommendations:", error)
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  const handleGridResponse = (gridData: APIResponse[][][]) => {
    setRecommendationsGrid((prev) => {
      const newGrid = prev.map((row) => row.map((cell) => ({ ...cell })))

      gridData.forEach((timeRow, timeIndex) => {
        timeRow.forEach((dayCell, dayIndex) => {
          if (Array.isArray(dayCell) && dayCell.length > 0) {
            const courseData = dayCell[0]
            if (courseData?.course_code) {
              newGrid[timeIndex][dayIndex] = {
                preference: (courseData.preferences as "preferred" | "unavailable") || "preferred",
                rank: courseData.rank || 1,
                course_code: courseData.course_code,
              }
            }
          }
        })
      })

      return newGrid
    })
  }

  const updateCell = (timeIndex: number, dayIndex: number, isRightClick: boolean) => {
    if (activeTab !== "preferences") return

    setPreferencesGrid((prev) => {
      const newGrid = prev.map((row) => row.map((cell) => ({ ...cell })))
      const currentCell = newGrid[timeIndex][dayIndex]

      if (isRightClick) {
        currentCell.preference = currentCell.preference === "unavailable" ? "default" : "unavailable"
        currentCell.rank = currentCell.preference === "unavailable" ? 5 : 3
      } else {
        if (currentCell.preference === "default") {
          currentCell.preference = "preferred"
          currentCell.rank = currentRank
        } else if (currentCell.preference === "preferred" && currentCell.rank < 3) {
          currentCell.rank += 1
        } else {
          currentCell.preference = "default"
          currentCell.rank = 3
        }
      }

      return newGrid
    })
  }

  const handleMouseDown = (timeIndex: number, dayIndex: number, isRightClick: boolean, e: React.MouseEvent) => {
    if (activeTab !== "preferences") return

    e.preventDefault()
    setIsDragging(true)
    setDragStartPosition({ timeIndex, dayIndex })
    setDragType(isRightClick ? "unavailable" : "preferred")
    mouseDownTimeRef.current = Date.now()
    updateCell(timeIndex, dayIndex, isRightClick)
  }

  const handleMouseEnter = (timeIndex: number, dayIndex: number) => {
    if (!isDragging || !dragType || !dragStartPosition || activeTab !== "preferences") return

    const minTime = Math.min(dragStartPosition.timeIndex, timeIndex)
    const maxTime = Math.max(dragStartPosition.timeIndex, timeIndex)
    const minDay = Math.min(dragStartPosition.dayIndex, dayIndex)
    const maxDay = Math.max(dragStartPosition.dayIndex, dayIndex)

    setPreferencesGrid((prev) => {
      const newGrid = prev.map((row) => row.map((cell) => ({ ...cell })))

      for (let tIdx = minTime; tIdx <= maxTime; tIdx++) {
        for (let dIdx = minDay; dIdx <= maxDay; dIdx++) {
          const cell = newGrid[tIdx][dIdx]
          if (dragType === "unavailable") {
            cell.preference = "unavailable"
            cell.rank = 5
          } else {
            cell.preference = "preferred"
            cell.rank = currentRank
          }
        }
      }

      return newGrid
    })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setDragType(null)
    setDragStartPosition(null)
  }

  const getCellStyling = (timeIndex: number, dayIndex: number) => {
    const currentGrid = getCurrentGrid()
    const cell = currentGrid[timeIndex][dayIndex]
    const baseClasses = `p-4 h-16 border-l border-purple-600/30 transition-all duration-150 select-none relative ${
      activeTab === "preferences" ? "cursor-pointer" : "cursor-default"
    }`

    if (cell.course_code) {
      return `${baseClasses} bg-blue-600/70 hover:bg-blue-600/80`
    }

    switch (cell.preference) {
      case "preferred":
        const intensity = cell.rank === 1 ? "600" : cell.rank === 2 ? "500" : "400"
        return `${baseClasses} bg-green-${intensity}/50 ${activeTab === "preferences" ? `hover:bg-green-${intensity}/60` : ""}`
      case "unavailable":
        return `${baseClasses} bg-red-600/40 ${activeTab === "preferences" ? "hover:bg-red-600/50" : ""}`
      default:
        return `${baseClasses} bg-purple-800/20 ${activeTab === "preferences" ? "hover:bg-purple-700/30" : ""}`
    }
  }

  const addCourse = () => {
    if (!courseCode.trim()) return
    setCourses([...courses, courseCode])
    setCourseCode("")
  }

  const clearPreferences = () => {
    setPreferencesGrid(initializeTimetable())
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900 w-screen">
      <header className="p-6 pb-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-light text-white">Semester 2 Timetable</h1>
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
              <Bell className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
              <User className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-white hover:bg-white/10">
              <Settings className="h-5 w-5" />
            </Button>
          </div>
        </div>

        <div className="flex items-center justify-between mb-6">
          <div className="relative">
            <Input
              placeholder="ADD A COURSE"
              className="w-80 bg-white/90 border-0 text-gray-700 placeholder:text-gray-500 pr-10"
              value={courseCode}
              onChange={handleChange}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault()
                  addCourse()
                }
              }}
            />
            <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
          </div>

          <div className="flex items-center gap-2">
            <div className="bg-purple-700/50 rounded-lg flex">
              <Button
                variant={activeTab === "preferences" ? "default" : "ghost"}
                size="sm"
                onClick={() => setActiveTab("preferences")}
                className={`rounded-r-none ${
                  activeTab === "preferences" ? "bg-purple-600 text-white" : "text-purple-200 hover:bg-purple-600/30"
                }`}
              >
                My Preferences
              </Button>
              <Button
                variant={activeTab === "recommendations" ? "default" : "ghost"}
                size="sm"
                onClick={() => setActiveTab("recommendations")}
                className={`rounded-l-none ${
                  activeTab === "recommendations"
                    ? "bg-purple-600 text-white"
                    : "text-purple-200 hover:bg-purple-600/30"
                }`}
              >
                Recommended
              </Button>
            </div>
          </div>
        </div>

        {activeTab === "preferences" && (
          <div className="mb-4 space-y-3">
            <div className="p-3 bg-purple-700/30 rounded-lg">
              <p className="text-purple-100 text-sm">
                <strong>Drag</strong> to select multiple time slots • <strong>Left-click</strong> for preferred times
                (green) • <strong>Right-click</strong> for unavailable times (red) • <strong>Click repeatedly</strong>{" "}
                to cycle through preference ranks
              </p>
            </div>

            <div className="flex items-center gap-4 p-3 bg-purple-700/20 rounded-lg">
              <span className="text-purple-100 text-sm font-medium">Preference Rank:</span>
              <div className="flex gap-2">
                {[1, 2, 3].map((rank) => (
                  <Button
                    key={rank}
                    size="sm"
                    variant={currentRank === rank ? "default" : "outline"}
                    onClick={() => setCurrentRank(rank)}
                    className={`text-xs ${currentRank === rank ? "bg-green-600 hover:bg-green-700" : "bg-purple-600/30 hover:bg-purple-600/50"}`}
                  >
                    Rank {rank} {"★".repeat(rank)}
                  </Button>
                ))}
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={clearPreferences}
                className="ml-auto bg-red-600/30 hover:bg-red-600/50 text-red-100"
              >
                Clear All
              </Button>
            </div>
          </div>
        )}

        {activeTab === "recommendations" && (
          <div className="mb-4">
            <div className="p-3 bg-purple-700/30 rounded-lg">
              <p className="text-purple-100 text-sm">
                <strong>Recommended Timetable</strong> - Generated based on your course selections and preferences.
                Switch to "My Preferences" tab to modify your time preferences.
              </p>
            </div>
          </div>
        )}
      </header>

      <div className="px-6 flex gap-6">
		{activeTab === "preferences" ?
        <div className="w-80 space-y-4">
          <div className="space-y-3">
            <Select defaultValue="S1" onValueChange={setSemester}>
              <SelectTrigger className="bg-purple-700/30 border-purple-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="S1">SEMESTER 1 2025</SelectItem>
                <SelectItem value="S2">SEMESTER 2 2025</SelectItem>
              </SelectContent>
            </Select>

            <Select defaultValue="STLUC" onValueChange={setLocation}>
              <SelectTrigger className="bg-purple-700/30 border-purple-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="STLUC">ST LUCIA</SelectItem>
                <SelectItem value="GATTN">GATTON</SelectItem>
              </SelectContent>
            </Select>

            <Select defaultValue="internal">
              <SelectTrigger className="bg-purple-700/30 border-purple-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="internal">INTERNAL</SelectItem>
                <SelectItem value="external">EXTERNAL</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="border-2 border-dashed border-purple-400/50 rounded-lg p-2 text-center flex flex-col gap-4">
            {courses.length == 0 ? (
              <>
                <div className="text-purple-200 text-sm font-medium p-2">
                  SEARCH TO ADD
                  <br />
                  COURSES
                </div>
              </>
            ) : (
              <div>
                {courses.map((course, index) => (
                  <div
                    key={index}
                    className="w-full border-2 border-purple-400/50 border-dashed rounded-lg h-16 mb-4 flex items-center justify-center"
                  >
                    <h1 className="text-sm text-purple-200 font-medium">{course}</h1>
                  </div>
                ))}
                <Button
                  onClick={recommendTimetable}
                  disabled={isLoadingRecommendations}
                  className="w-full bg-green-600 hover:bg-green-700 text-white"
                >
                  {isLoadingRecommendations ? "Loading..." : "Get Best Timetable"}
                </Button>
              </div>
            )}
          </div>

          <Button
            onClick={addCourse}
            className="w-full bg-purple-600 hover:bg-purple-500 text-white"
            disabled={!courseCode.trim()}
          >
            Add Course
          </Button>
        </div> : 
		<div className="w-80 space-y-4">

		</div> 
		}

        <div className="flex-1">
          <div
            className="bg-purple-800/30 rounded-lg overflow-hidden select-none"
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ userSelect: "none" }}
          >
            <div className="grid grid-cols-6 bg-purple-700/50">
              <div className="p-3"></div>
              {days.map((day) => (
                <div key={day} className="p-3 text-center text-white font-medium text-sm">
                  {day}
                </div>
              ))}
            </div>

            {timeSlots.map((time, timeIndex) => (
              <div key={time} className="grid grid-cols-6 border-t border-purple-600/30">
                <div className="p-4 text-white font-medium text-sm bg-purple-700/20 flex items-center justify-center">
                  {time}
                </div>
                {days.map((day, dayIndex) => {
                  const currentGrid = getCurrentGrid()
                  const cell = currentGrid[timeIndex][dayIndex]

                  return (
                    <div
                      key={`${dayIndex}-${timeIndex}`}
                      className={getCellStyling(timeIndex, dayIndex)}
                      onMouseDown={(e) => handleMouseDown(timeIndex, dayIndex, e.button === 2, e)}
                      onMouseEnter={() => handleMouseEnter(timeIndex, dayIndex)}
                      onContextMenu={(e) => e.preventDefault()}
                      style={{
                        backgroundImage:
                          cell.preference === "default" && !cell.course_code
                            ? `repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(147, 51, 234, 0.1) 2px, rgba(147, 51, 234, 0.1) 4px)`
                            : undefined,
                      }}
                    >
                      {cell.course_code && (
                        <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-sm pointer-events-none">
                          {cell.course_code}
                        </div>
                      )}
                      {cell.preference === "unavailable" && !cell.course_code && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-red-200 text-xl font-bold">×</div>
                        </div>
                      )}
                      {cell.preference === "preferred" && !cell.course_code && (
                        <div className="absolute top-1 right-1">
                          <div className="text-green-200 text-xs font-bold">{cell.rank}</div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

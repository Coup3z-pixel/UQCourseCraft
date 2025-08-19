import { Search, Trash, AlertCircleIcon, Info, X } from "lucide-react"
import { Button } from "./components/ui/button"
import { Input } from "./components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select"
import { useState, useRef, useEffect } from "react"
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert"

const timeSlots = [
  "08:00-08:30",
  "08:30-09:00",
  "09:00-09:30",
  "09:30-10:00",
  "10:00-10:30",
  "10:30-11:00",
  "11:00-11:30",
  "11:30-12:00",
  "12:00-12:30",
  "12:30-13:00",
  "13:00-13:30",
  "13:30-14:00",
  "14:00-14:30",
  "14:30-15:00",
  "15:00-15:30",
  "15:30-16:00",
  "16:00-16:30",
  "16:30-17:00",
  "17:00-17:30",
  "17:30-18:00",
  "18:00-18:30",
  "18:30-19:00",
  "19:00-19:30",
  "19:30-20:00",
  "20:00-20:30",
  "20:30-21:00",
  "21:00-21:30",
  "21:30-22:00",
]
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

type RecommendationOption = {
  id: string
  name: string
  score: number
  conflicts: number
  grid: CellState[][]
}

const defaultCellState: CellState = {
  preference: "preferred",
  rank: 4,
}

export default function TimetablePage() {
  const initializeTimetable = (): CellState[][] => {
    return timeSlots.map(() => days.map(() => ({ ...defaultCellState })))
  }

  const [showInfoModal, setShowInfoModal] = useState(false)

  useEffect(() => {
    setShowInfoModal(true)
  }, [])

  const [activeTab, setActiveTab] = useState<"preferences" | "recommendations">("preferences")
  const [preferencesGrid, setPreferencesGrid] = useState<CellState[][]>(initializeTimetable())
  const [recommendationsGrid, setRecommendationsGrid] = useState<CellState[][]>(initializeTimetable())

  const [recommendationOptions, setRecommendationOptions] = useState<RecommendationOption[]>([])
  const [selectedRecommendation, setSelectedRecommendation] = useState<string | null>(null)

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
  const [attendLectures, setAttendLectures] = useState(true)

	const [showAlert, setShowAlert] = useState(false);
	const [alertTitle, setAlertTitle] = useState("");
	const [alertDescription, setAlertDescription] = useState("")

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
          attendLectures,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        handleMultipleRecommendations(data)
        setActiveTab("recommendations")
      } else {
		  setAlertTitle("Can't find a viable timetable")
		  setAlertDescription("Please be less specific about your preferences. We can't find a timetable with your current preferences")
		  setShowAlert(true)

			setTimeout(() => {
			  setShowAlert(false);
			}, 2000); // Hide after 3 seconds


	  }
    } catch (error) {
      console.error("Failed to load recommendations:", error)
    } finally {
      setIsLoadingRecommendations(false)
    }
  }

  const handleMultipleRecommendations = (apiData: any) => {
    // Handle both single recommendation and multiple recommendations
    if (Array.isArray(apiData.recommendations)) {
      // Multiple recommendations format
      const options: RecommendationOption[] = apiData.recommendations.map((rec: any, index: number) => ({
        id: rec.id || `rec_${index}`,
        name: rec.name || `Option ${index + 1}`,
        score: rec.score || 0,
        conflicts: rec.conflicts || 0,
        grid: convertAPIResponseToGrid(rec.grid || rec.schedule || []),
      }))

      setRecommendationOptions(options)
      if (options.length > 0) {
        setSelectedRecommendation(options[0].id)
        setRecommendationsGrid(options[0].grid)
      }
    } else {
      // Single recommendation format (backward compatibility)
      const singleOption: RecommendationOption = {
        id: "single_rec",
        name: "Recommended Timetable",
        score: 95,
        conflicts: 0,
        grid: convertAPIResponseToGrid(apiData),
      }

      setRecommendationOptions([singleOption])
      setSelectedRecommendation("single_rec")
      setRecommendationsGrid(singleOption.grid)
    }
  }

  const convertAPIResponseToGrid = (gridData: APIResponse[][][]): CellState[][] => {
    const newGrid = initializeTimetable()

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
  } 

  const selectRecommendation = (recommendationId: string) => {
    const selected = recommendationOptions.find((opt) => opt.id === recommendationId)
    if (selected) {
      setSelectedRecommendation(recommendationId)
      setRecommendationsGrid(selected.grid)
    }
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
    setDragType("preferred")
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
    const baseClasses = `p-2 h-full border-l border-purple-600/30 transition-all duration-150 select-none relative border-t ${
      activeTab === "preferences" ? "cursor-pointer" : "cursor-default"
    }`

    if (cell.course_code) {
      return `${baseClasses} bg-purple-600/70 hover:bg-purple-600/80`
    }

	// `bg-green-600/50 bg-green-500/50 bg-green-400/50`
    switch (cell.preference) {
      case "preferred":
        const intensity = cell.rank === 1 ? "green-400/50" : cell.rank === 2 ? "green-500/50" : cell.rank === 3 ? "green-600/50" : ""
        return `${baseClasses} bg-${intensity}`
      case "unavailable":
        return `${baseClasses} bg-red-600/40 ${activeTab === "preferences" ? "hover:bg-red-600/50" : ""}`
      default:
        return `${baseClasses} bg-purple-800/20 ${activeTab === "preferences" ? "hover:bg-purple-700/30" : ""}`
    }
  }

	const addCourse = async () => {
		if (!courseCode.trim()) return

		let course_response = await fetch(`http://127.0.0.1:5000/course/${courseCode}?semester=${semester}&location=${location}`)

		if (!course_response.ok) {
			setAlertTitle("Make sure the right settings")
			setAlertDescription("Sorry but we can't find the course that you are specificying")
			setShowAlert(true)

			setTimeout(() => {
			  setShowAlert(false);
			}, 2000); // Hide after 3 seconds

			return
		}

		if (courses.includes(courseCode)) {
			setAlertTitle("Make sure the right settings")
			setAlertDescription("Sorry but we can't find the course that you are specifying")
			setShowAlert(true)

			setTimeout(() => {
			  setShowAlert(false);
			}, 2000); // Hide after 3 seconds

			return

		}

		setCourses([...courses, courseCode])
		setCourseCode("")
	}

	useEffect(() => {
		// Optional: Auto-hide the alert after a few seconds
		const timer = setTimeout(() => {
		  setShowAlert(false);
		}, 4000); // Hide after 3 seconds

		return () => clearTimeout(timer);
	  }, []);


  const clearAll = () => {
    setPreferencesGrid(initializeTimetable())
  }

  const removeThisCourse = (index: number) => {
	  const updateCourses = [...courses]
	  updateCourses.splice(index, 1)
	  setCourses(updateCourses)
  }

  return (
	<div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900 w-screen flex items-center">
			<Alert
			  className={`
				data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95
				data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95
				absolute top-4 right-4 w-96 transition-opacity duration-500
				text-white bg-purple-500 ${ showAlert ? "opacity-100" : "opacity-0" }
			  `}

			  variant={"destructive"}
			  // You might need to add an `onAnimationEnd` to truly unmount the component after the animation finishes
			  // For a simple fade out, the `data-[state=closed]` classes are applied when `showAlert` becomes false
			>
				<AlertCircleIcon />
			  <AlertTitle>{alertTitle}</AlertTitle>
			  <AlertDescription>
				{alertDescription}
			  </AlertDescription>
			</Alert>


	{showInfoModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-purple-800 rounded-lg p-6 max-w-md w-full border border-purple-600 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Info className="h-5 w-5 text-purple-300" />
                <h2 className="text-xl font-semibold text-white">How to Use Timetable</h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowInfoModal(false)}
                className="text-purple-300 hover:bg-purple-700/50"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-4 text-purple-100 text-sm">
              <div>
                <h3 className="font-medium text-white mb-2">Getting Started:</h3>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Add course codes in the search bar and press Enter</li>
                  <li>Select your semester, campus location, and preferences</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-white mb-2">Setting Preferences:</h3>
                <ul className="space-y-1 list-disc list-inside">
                  <li>
                    <strong>Left-click & drag:</strong> Mark preferred time slots (green)
                  </li>
                  <li>
                    <strong>Right-click & drag:</strong> Mark unavailable times (red)
                  </li>
                  <li>Use Rank 1-3 buttons to set preference priority</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-white mb-2">Getting Recommendations:</h3>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Click "Get Recommendations" to generate timetable options</li>
                  <li>Switch between "My Preferences" and "Recommended" tabs</li>
                  <li>Select different recommendation options from the dropdown</li>
                </ul>
              </div>
            </div>

            <Button
              onClick={() => setShowInfoModal(false)}
              className="w-full mt-6 bg-purple-600 hover:bg-purple-500 text-white"
            >
              Got it!
            </Button>
          </div>
        </div>
      )}
 
      <div className="px-6 flex gap-6 w-full h-screen py-4">
        <div className="w-80 space-y-4 overflow-auto">
<div className="flex items-center justify-between mb-6">
			<div className="flex items-center h-8">
				<img src="/favicon.png" alt="" className="h-full aspect-square bg-white rounded-md"/>
				<h1 className="text-3xl font-light text-white ml-2">UQ Course Craft</h1>
			</div>
          
			<div className="flex items-center gap-3">
				<Button
				  variant="ghost"
				  size="icon"
				  className="text-white hover:bg-white/10 z-10"
				  onClick={() => setShowInfoModal(true)}
				>
				  <Info className="h-5 w-5" />
				</Button>
            </div>
        </div>

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

{activeTab === "preferences" && (
          <div className="mb-4 text-purple-200 text-sm">
            <strong>My Preferences</strong> - Left-click and drag to mark preferred times. Right-click and drag to mark
            unavailable times.
          </div>
        )}

        {activeTab === "recommendations" && (
          <div className="mb-4 text-purple-200 text-sm">
            <strong>Recommended Timetable</strong> - Generated based on your course selections and preferences. Switch
            to "My Preferences" tab to modify your time preferences.
          </div>
        )}

          <div className="space-y-3 flex">
			<div>
				<Select value={semester} onValueChange={setSemester}>
				  <SelectTrigger className="bg-purple-700/50 border-purple-400 text-white text-sm font-medium">
					<SelectValue placeholder="Select semester" />
				  </SelectTrigger>
				  <SelectContent className="bg-purple-800 border-purple-600">
					<SelectItem value="S1" className="text-white hover:bg-purple-700 focus:bg-purple-700">
					  SEMESTER 1
					</SelectItem>
					<SelectItem value="S2" className="text-white hover:bg-purple-700 focus:bg-purple-700">
					  SEMESTER 2
					</SelectItem>
				  </SelectContent>
				</Select>
			</div>
			<div className="ml-4">
				<Select value={location} onValueChange={setLocation}>
				  <SelectTrigger className="bg-purple-700/50 border-purple-400 text-white text-sm font-medium">
					<SelectValue placeholder="Select location" />
				  </SelectTrigger>
				  <SelectContent className="bg-purple-800 border-purple-600">
					<SelectItem value="STLUC" className="text-white hover:bg-purple-700 focus:bg-purple-700">
					  ST LUCIA
					</SelectItem>
					<SelectItem value="GATTN" className="text-white hover:bg-purple-700 focus:bg-purple-700">
					  GATTON
					</SelectItem>
					<SelectItem value="HERST" className="text-white hover:bg-purple-700 focus:bg-purple-700">
					  HERSTON
					</SelectItem>
				  </SelectContent>
				</Select>
			</div> 
          </div>

          {activeTab === "preferences" && (
            <div className="space-y-3">
              <div className="text-white text-sm font-medium">Preference Rank:</div>
              <div className="flex gap-2">
                {[1, 2, 3, 4].map((rank) => (
                  <Button
                    key={rank}
                    variant={currentRank === rank ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentRank(rank)}
                    className={`${
                      currentRank === rank
                        ? "bg-green-600 text-white"
                        : "border-green-400 text-green-400 hover:bg-green-600/20"
                    }`}
                  >
                    {rank === 1 ? "Ideal" : rank === 2 ? "Good" : rank === 3 ? "Bad" : "Try to Avoid"}
                  </Button>
                ))}
              </div>
              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="attend-lectures"
                  checked={attendLectures}
                  onChange={(e) => setAttendLectures(e.target.checked)}
                  className="w-4 h-4 text-purple-600 bg-purple-700/50 border-purple-400 rounded focus:ring-purple-500 focus:ring-2"
                />
                <label htmlFor="attend-lectures" className="text-white text-sm">
                  I want to attend lectures
                </label>
              </div>
              <Button
                onClick={clearAll}
                variant="outline"
                size="sm"
                className="w-full border-red-400 text-red-400 hover:bg-red-600/20 bg-transparent"
              >
                Clear All
              </Button>
            </div>
          )}

          {activeTab === "recommendations" && recommendationOptions.length > 0 && (
            <div className="space-y-3">
              <div className="text-white text-sm font-medium">Recommendation Options:</div>
              <Select value={selectedRecommendation || ""} onValueChange={selectRecommendation}>
                <SelectTrigger className="w-full bg-purple-700/50 border-purple-400 text-white">
                  <SelectValue placeholder="Select a recommendation" />
                </SelectTrigger>
                <SelectContent className="bg-purple-800 border-purple-600">
                  {recommendationOptions.map((option) => (
                    <SelectItem
                      key={option.id}
                      value={option.id}
                      className="text-white hover:bg-purple-700 focus:bg-purple-700"
                    >
                      <div className="flex flex-col">
                        <div className="font-medium">{option.name}</div>
                        <div className="text-xs opacity-80">
                          Score: {option.score} | Conflicts: {option.conflicts}
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {activeTab === "recommendations" && recommendationOptions.length === 0 && (
            <div className="space-y-3">
              <div className="text-white text-sm font-medium">Recommendation Options:</div>
              <div className="border-2 border-dashed border-purple-400/50 rounded-lg p-4 text-center">
                <div className="text-purple-200 text-sm">
                  No recommendations loaded yet.
                  <br />
                  Add courses and click "Get Recommendations" to see options.
                </div>
              </div>
            </div>
          )}

          <div className="border-2 border-dashed border-purple-400/50 rounded-lg p-4 text-center min-h-[200px] flex flex-col items-center justify-center">
            {courses.length === 0 ? (
              <div className="text-purple-200 text-sm font-medium">
                SEARCH TO ADD
                <br />
                COURSES
              </div>
            ) : (
              <div className="w-full space-y-3">
                {courses.map((course, index) => (
                  <div
                    key={index}
                    className="w-full border-2 border-purple-400/50 border-dashed rounded-lg h-12 flex items-center justify-center px-2"
                  >
                    <span className="text-sm text-purple-200 font-medium">{course}</span>
						<Button 
							className="ml-auto"
							onClick={() => { removeThisCourse(index) }}
						>
							<Trash className="text-white"/>
						</Button>
                  </div>
                ))}
                <Button
                  onClick={recommendTimetable}
                  disabled={isLoadingRecommendations}
                  className="w-full bg-purple-600 hover:bg-purple-500 text-white mt-4"
                >
                  {isLoadingRecommendations ? "Loading..." : "Get Recommendations"}
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Existing timetable grid code */}
        <div className="flex-1">
          <div
            className="bg-purple-800/30 rounded-lg overflow-hidden select-none h-full flex flex-col relative"
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ userSelect: "none" }}
          >
            <div className="grid grid-cols-6 bg-purple-700/50 grow">
              <div className=""></div>
              {days.map((day) => (
                <div key={day} className="p-1 text-center text-white font-medium text-sm">
                  {day}
                </div>
              ))}
            </div>

            {timeSlots.map((time, timeIndex) => (
              <div key={timeIndex} className="grid grid-cols-6  grow">
                <div className="text-white font-medium text-xs bg-purple-700/20 flex items-center justify-center">
                  {time}
                </div>
                {days.map((_, dayIndex) => {
                  const currentGrid = getCurrentGrid()
                  const cell = currentGrid[timeIndex][dayIndex]

                  return (
                    <div
                      key={`${dayIndex}-${timeIndex}`}
                      className={getCellStyling(timeIndex, dayIndex) + ` border-t`}
                      onMouseDown={(e) => handleMouseDown(timeIndex, dayIndex, e.button === 2, e)}
                      onMouseEnter={() => handleMouseEnter(timeIndex, dayIndex)}
                      onContextMenu={(e) => e.preventDefault()}
                      style={{
                        backgroundImage:
                          cell.rank === 4 && !cell.course_code
                            ? `repeating-linear-gradient(45deg, transparent, transparent 2px, rgba(147, 51, 234, 0.15) 2px, rgba(147, 51, 234, 0.15) 4px)`
                            : undefined,
                      }}
                    >
                      {cell.course_code && (
                        <div className="absolute inset-0 flex items-center justify-center text-white font-bold text-xs pointer-events-none">
							{timeIndex == 0 ? cell.course_code : (cell.course_code != currentGrid[timeIndex-1][dayIndex].course_code ? cell.course_code : "")}			
                        </div>
                      )}
                      {cell.preference === "unavailable" && !cell.course_code && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-red-200 text-lg font-bold">×</div>
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

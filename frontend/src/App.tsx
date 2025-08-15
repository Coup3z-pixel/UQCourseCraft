import { Search, Plus, User, Bell, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useState, useRef } from "react"

import "./App.css"

const timeSlots = ["8", "9", "10", "11", "12", "1", "2", "3", "4", "5", "6"]
const days = ["MON", "TUE", "WED", "THU", "FRI"]

type CellState = {
  preference: "default" | "preferred" | "unavailable"
  rank: number // 1-5 ranking system, 1 being highest preference
}

const defaultCellState: CellState = {
  preference: "default",
  rank: 3 // neutral ranking
}

function App() {
	// Initialize 2D array: [timeSlot][day]
	const initializeTimetable = (): CellState[][] => {
		return timeSlots.map(() => 
			days.map(() => ({ ...defaultCellState }))
		)
	}

	const [timetableGrid, setTimetableGrid] = useState<CellState[][]>(initializeTimetable())
	const [isDragging, setIsDragging] = useState(false)
	const [dragType, setDragType] = useState<"preferred" | "unavailable" | null>(null)
	const [dragStartPosition, setDragStartPosition] = useState<{timeIndex: number, dayIndex: number} | null>(null)
	const [hasMouseMoved, setHasMouseMoved] = useState(false)
	const [currentRank, setCurrentRank] = useState(1) // Current rank being applied
	const mouseDownTimeRef = useRef<number>(0)
	const dragThresholdRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 })

	const [courseCode, setCourseCode] = useState("");
	const [courses, setCourses] = useState<string[]>([])

	const [semester, setSemester] = useState("S1")
	const [location, setLocation] = useState("STLUC")
	const [attendance, setAttendance] = useState("")

	const handleChange = (event) => {
		setCourseCode(capitalizeCourse(event.target.value));
	};

	const capitalizeCourse = (code) => {
	  return code
		.toLowerCase()
		.split('')
		.map(course => course.charAt(0).toUpperCase() + course.slice(1))
		.join('');
	}

	const convertTimetableForAPI = () => {
		const preferences: Record<string, { preference: string, rank: number }> = {}
		
		timetableGrid.forEach((timeRow, timeIndex) => {
			timeRow.forEach((cell, dayIndex) => {
				if (cell.preference !== "default") {
					const cellKey = `${days[dayIndex]}-${timeSlots[timeIndex]}`
					preferences[cellKey] = {
						preference: cell.preference,
						rank: cell.rank
					}
				}
			})
		})
		
		return preferences
	}

	const recommendTimetable = async () => {
		let url = `http://127.0.0.1:5000/timetable`
		let timetableRequest = await fetch(url, {
			method: "POST",
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				courses: courses,
				timetablePreferences: convertTimetableForAPI()
			})
		})
		
		if (timetableRequest.ok) {
			let response = await timetableRequest.json()
			console.log("Recommended timetable:", response)
		}
	}

	const handleEnterPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
		if (event.key === "Enter") {
			event.preventDefault(); 
			addCourse()
		}
	};

	const addCourse = async () => {
		if (!courseCode.trim()) return
		
		let url = `http://127.0.0.1:5000/course/${courseCode}?semester=${semester}&location=${location}`;
		console.log(url)
		try {
			let courseRequest = await fetch(url);
			let courseResponse = await courseRequest.json()
			console.log(courseResponse)
			setCourses([...courses, courseCode])
			setCourseCode("") // Clear input after adding
		} catch (error) {
			console.error("Error adding course:", error)
		}
	}

	const handleSemesterChange = (event) => { setSemester(event) }
	const handleLocationChange = (event) => { setLocation(event) }
	const handleAttendanceChange = (event) => { setAttendance(event) }

	const updateCell = (timeIndex: number, dayIndex: number, isRightClick: boolean) => {
		setTimetableGrid((prev) => {
			const newGrid = prev.map(row => row.map(cell => ({ ...cell })))
			const currentCell = newGrid[timeIndex][dayIndex]

			if (isRightClick) {
				// Right click toggles unavailable
				if (currentCell.preference === "unavailable") {
					currentCell.preference = "default"
					currentCell.rank = 3
				} else {
					currentCell.preference = "unavailable"
					currentCell.rank = 5 // Lowest preference
				}
			} else {
				// Left click cycles through preferred states with different ranks
				if (currentCell.preference === "default") {
					currentCell.preference = "preferred"
					currentCell.rank = currentRank
				} else if (currentCell.preference === "preferred") {
					// Cycle through ranks 1-3 for preferred, then back to default
					if (currentCell.rank < 3) {
						currentCell.rank = currentCell.rank + 1
					} else {
						currentCell.preference = "default"
						currentCell.rank = 3
					}
				} else {
					currentCell.preference = "preferred"
					currentCell.rank = currentRank
				}
			}

			return newGrid
		})
	}

	const handleMouseDown = (timeIndex: number, dayIndex: number, isRightClick: boolean, event: React.MouseEvent) => {
		event.preventDefault()
		
		setIsDragging(true)
		setDragStartPosition({ timeIndex, dayIndex })
		setDragType(isRightClick ? "unavailable" : "preferred")
		setHasMouseMoved(false)
		mouseDownTimeRef.current = Date.now()
		
		// Store initial mouse position for drag threshold
		dragThresholdRef.current = { x: event.clientX, y: event.clientY }

		// Apply initial state to the clicked cell immediately for better responsiveness
		updateCell(timeIndex, dayIndex, isRightClick)
	}

	const handleMouseEnter = (timeIndex: number, dayIndex: number, event?: React.MouseEvent) => {
		if (!isDragging || !dragType || !dragStartPosition) return

		// Check if mouse has moved enough to be considered a drag
		if (event && !hasMouseMoved) {
			const deltaX = Math.abs(event.clientX - dragThresholdRef.current.x)
			const deltaY = Math.abs(event.clientY - dragThresholdRef.current.y)
			
			// Only start dragging if mouse has moved more than 3 pixels
			if (deltaX > 3 || deltaY > 3) {
				setHasMouseMoved(true)
			} else {
				return // Don't drag yet
			}
		}

		// Get the range of cells from start to current
		const minTime = Math.min(dragStartPosition.timeIndex, timeIndex)
		const maxTime = Math.max(dragStartPosition.timeIndex, timeIndex)
		const minDay = Math.min(dragStartPosition.dayIndex, dayIndex)
		const maxDay = Math.max(dragStartPosition.dayIndex, dayIndex)

		setTimetableGrid((prev) => {
			const newGrid = prev.map(row => row.map(cell => ({ ...cell })))

			// Apply drag type to all cells in the selection rectangle
			for (let tIdx = minTime; tIdx <= maxTime; tIdx++) {
				for (let dIdx = minDay; dIdx <= maxDay; dIdx++) {
					if (dragType === "unavailable") {
						newGrid[tIdx][dIdx].preference = "unavailable"
						newGrid[tIdx][dIdx].rank = 5
					} else {
						newGrid[tIdx][dIdx].preference = "preferred"
						newGrid[tIdx][dIdx].rank = currentRank
					}
				}
			}

			return newGrid
		})
	}

	const handleMouseUp = () => {
		// If it was a very short click without movement, treat it as a single cell toggle
		if (!hasMouseMoved && dragStartPosition && Date.now() - mouseDownTimeRef.current < 200) {
			// The cell state was already updated in mouseDown, so we don't need to do anything else
		}

		setIsDragging(false)
		setDragType(null)
		setDragStartPosition(null)
		setHasMouseMoved(false)
	}

	const getCellStyling = (timeIndex: number, dayIndex: number) => {
		const cell = timetableGrid[timeIndex][dayIndex]
		const baseClasses = "p-4 h-16 border-l border-purple-600/30 transition-all duration-150 cursor-pointer select-none relative"

		switch (cell.preference) {
			case "preferred":
				// Different shades of green based on rank (1=darkest, 3=lightest)
				const greenIntensity = cell.rank === 1 ? "600" : cell.rank === 2 ? "500" : "400"
				const hoverIntensity = cell.rank === 1 ? "700" : cell.rank === 2 ? "600" : "500"
				return `${baseClasses} bg-green-${greenIntensity}/50 hover:bg-green-${hoverIntensity}/60 shadow-sm`
			case "unavailable":
				return `${baseClasses} bg-red-600/40 hover:bg-red-600/50 shadow-sm`
			default:
				return `${baseClasses} bg-purple-800/20 hover:bg-purple-700/30`
		}
	}

	const getRankDisplay = (rank: number) => {
		const stars = "★".repeat(rank) + "☆".repeat(5 - rank)
		return stars
	}

	const clearAllPreferences = () => {
		setTimetableGrid(initializeTimetable())
	}

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900 w-screen">
      {/* Header */}
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

        {/* Search and Tab Section */}
        <div className="flex items-center justify-between mb-6">
          <div className="relative">
            <Input
              placeholder="ADD A COURSE"
              className="w-80 bg-white/90 border-0 text-gray-700 placeholder:text-gray-500 pr-10"
			  value={courseCode}
			  onChange={handleChange}
			  onKeyDown={handleEnterPress}
            />
            <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500" />
          </div>

          <div className="flex items-center gap-2">
            <div className="bg-purple-700/50 rounded-lg px-4 py-2 flex items-center gap-2">
              <span className="text-white text-sm">Semester 2 Timetable</span>
              <Button variant="ghost" size="icon" className="h-6 w-6 text-white hover:bg-white/10">
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Instructions and Controls */}
        <div className="mb-4 space-y-3">
          <div className="p-3 bg-purple-700/30 rounded-lg">
            <p className="text-purple-100 text-sm">
              <strong>Drag</strong> to select multiple time slots • <strong>Left-click</strong> for preferred times (green) • <strong>Right-click</strong> for unavailable times (red) • <strong>Click repeatedly</strong> to cycle through preference ranks
            </p>
          </div>
          
          {/* Rank Selector */}
          <div className="flex items-center gap-4 p-3 bg-purple-700/20 rounded-lg">
            <span className="text-purple-100 text-sm font-medium">Preference Rank:</span>
            <div className="flex gap-2">
              {[1, 2, 3].map((rank) => (
                <Button
                  key={rank}
                  size="sm"
                  variant={currentRank === rank ? "default" : "outline"}
                  onClick={() => setCurrentRank(rank)}
                  className={`text-xs ${currentRank === rank ? 'bg-green-600 hover:bg-green-700' : 'bg-purple-600/30 hover:bg-purple-600/50'}`}
                >
                  Rank {rank} {getRankDisplay(rank).slice(0, rank)}
                </Button>
              ))}
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={clearAllPreferences}
              className="ml-auto bg-red-600/30 hover:bg-red-600/50 text-red-100"
            >
              Clear All
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="px-6 flex gap-6">
        {/* Left Sidebar */}
        <div className="w-80 space-y-4">
          {/* Filters */}
          <div className="space-y-3">
            <Select 
				defaultValue="S1"
				onValueChange={handleSemesterChange}
			>
              <SelectTrigger className="bg-purple-700/30 border-purple-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="S1">SEMESTER 1 2025</SelectItem>
                <SelectItem value="S2">SEMESTER 2 2025</SelectItem>
              </SelectContent>
            </Select>

            <Select 
				defaultValue="STLUC"
				onValueChange={handleLocationChange}
			>
              <SelectTrigger className="bg-purple-700/30 border-purple-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="STLUC">ST LUCIA</SelectItem>
                <SelectItem value="GATTN">GATTON</SelectItem>
              </SelectContent>
            </Select>

            <Select 
				defaultValue="internal"
				onValueChange={handleAttendanceChange}
			>
              <SelectTrigger className="bg-purple-700/30 border-purple-600 text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="internal">INTERNAL</SelectItem>
                <SelectItem value="external">EXTERNAL</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Course Search Area */}
          <div className="border-2 border-dashed border-purple-400/50 rounded-lg p-2 text-center flex flex-col gap-4">
				{courses.length == 0 ? 
					(
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
								<div key={index} className="w-full border-2 border-purple-400/50 border-dashed rounded-lg h-16 mb-4 flex items-center justify-center">
									<h1 className="text-sm text-purple-200 font-medium">{course}</h1>
								</div>
							))}
							<Button 
								onClick={recommendTimetable}
								className="w-full bg-green-600 hover:bg-green-700 text-white"
							>
								Get Best Timetable
							</Button>
						</div>	
					)
				}
          </div>

          {/* Add Course Button */}
          <Button 
            onClick={addCourse} 
            className="w-full bg-purple-600 hover:bg-purple-500 text-white"
            disabled={!courseCode.trim()}
          >
            Add Course
          </Button>
        </div>

        {/* Timetable Grid */}
        <div className="flex-1">
          <div
            className="bg-purple-800/30 rounded-lg overflow-hidden select-none"
            onMouseUp={() => handleMouseUp()}
            onMouseLeave={() => handleMouseUp()}
            style={{ userSelect: 'none' }}
          >
            {/* Days Header */}
            <div className="grid grid-cols-6 bg-purple-700/50">
              <div className="p-3"></div>
              {days.map((day) => (
                <div key={day} className="p-3 text-center text-white font-medium text-sm">
                  {day}
                </div>
              ))}
            </div>

            {/* Time Slots */}
            {timeSlots.map((time, timeIndex) => (
              <div key={time} className="grid grid-cols-6 border-t border-purple-600/30">
                <div className="p-4 text-white font-medium text-sm bg-purple-700/20 flex items-center justify-center">
                  {time}
                </div>
                {days.map((day, dayIndex) => {
                  const cell = timetableGrid[timeIndex][dayIndex]

                  return (
                    <div
                      key={`${dayIndex}-${timeIndex}`}
                      className={getCellStyling(timeIndex, dayIndex)}
                      onMouseDown={(e) => {
                        handleMouseDown(timeIndex, dayIndex, e.button === 2, e)
                      }}
                      onMouseEnter={(e) => handleMouseEnter(timeIndex, dayIndex, e)}
                      onMouseUp={() => handleMouseUp()}
                      onContextMenu={(e) => {
                        e.preventDefault()
                      }}
                      style={{
                        backgroundImage:
                          cell.preference === "default"
                            ? `repeating-linear-gradient(
                          45deg,
                          transparent,
                          transparent 2px,
                          rgba(147, 51, 234, 0.1) 2px,
                          rgba(147, 51, 234, 0.1) 4px
                        )`
                            : undefined,
                      }}
                    >
                      {cell.preference === "unavailable" && (
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-red-200 text-xl font-bold">×</div>
                        </div>
                      )}
                      {cell.preference === "preferred" && (
                        <div className="absolute top-1 right-1">
                          <div className="text-green-200 text-xs font-bold">
                            {cell.rank}
                          </div>
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

export default App

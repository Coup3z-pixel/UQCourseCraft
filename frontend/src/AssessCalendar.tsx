import { Search, Trash, Calendar, List, Download, Info, X, Plus, Clock, BookOpen, AlertCircle } from "lucide-react"
import { Button } from "./components/ui/button"
import { Input } from "./components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select"
import { useState, useEffect } from "react"
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert"

type Assessment = {
  id: string
  courseCode: string
  courseName: string
  assessmentName: string
  dueDate: string
  weighting: number
  notes?: string
  type: "assignment" | "exam" | "quiz" | "project"
}

type Course = {
  code: string
  name: string
  semester: string
}



export default function AssessmentCalendar() {
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [viewMode, setViewMode] = useState<"list" | "calendar">("list")
  const [courseCode, setCourseCode] = useState("")
  const [courses, setCourses] = useState<Course[]>([])
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [semester, setSemester] = useState("S1")
  const [location, setLocation] = useState("STLUC")
  const [selectedAssessment, setSelectedAssessment] = useState<Assessment | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  const [showAlert, setShowAlert] = useState(false)
  const [alertTitle, setAlertTitle] = useState("")
  const [alertDescription, setAlertDescription] = useState("")

  useEffect(() => {
    setShowInfoModal(true)
  }, [])

  const capitalizeCourse = (code: string): string => {
    return code.toUpperCase()
  }

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCourseCode(capitalizeCourse(event.target.value))
  }

  const addCourse = async () => {
    if (!courseCode.trim()) return

    if (courses.some(course => course.code === courseCode)) {
      setAlertTitle("Course Already Added")
      setAlertDescription("This course is already in your list")
      setShowAlert(true)
      setTimeout(() => setShowAlert(false), 3000)
      return
    }

    setIsLoading(true)
    
    try {
      const response = await fetch(`http://localhost:5000/course/${courseCode}?semester=${semester}&location=${location}`)

      if (!response.ok) {
        setAlertTitle("Course Not Found")
        setAlertDescription("Please check the course code, semester, and location.")
        setShowAlert(true)
        setTimeout(() => setShowAlert(false), 3000)
        setIsLoading(false)
        return
      }

      const courseData = await response.json()
      const courseKey = Object.keys(courseData)[0]
      const courseName = courseKey ? courseKey.split('|')[1] : 'Course Name'

      const newCourse: Course = {
        code: courseCode,
        name: courseName,
        semester
      }

      setCourses([...courses, newCourse])
      
      const assessmentResponse = await fetch(`http://localhost:5000/assessment/${courseCode}?semester=${semester}&location=${location}`)
      if (assessmentResponse.ok) {
        const newAssessments = await assessmentResponse.json()
        setAssessments(prev => [...prev, ...newAssessments])
      } else {
        console.error("Could not fetch assessments for", courseCode)
        setAlertTitle("Assessments Not Found")
        setAlertDescription(`Could not retrieve assessments for ${courseCode}.`)
        setShowAlert(true)
        setTimeout(() => setShowAlert(false), 3000)
      }
      
      setCourseCode("")
    } catch (error) {
      console.error("Error verifying course:", error)
      setAlertTitle("Error")
      setAlertDescription("Could not connect to the server to verify the course.")
      setShowAlert(true)
      setTimeout(() => setShowAlert(false), 3000)
    } finally {
      setIsLoading(false)
    }
  }

  const removeCourse = (index: number) => {
    const courseToRemove = courses[index]
    const updatedCourses = [...courses]
    updatedCourses.splice(index, 1)
    setCourses(updatedCourses)
    
    // Remove assessments for this course
    setAssessments(prev => prev.filter(a => a.courseCode !== courseToRemove.code))
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) {
      return dateString
    }
    return date.toLocaleDateString('en-AU', { 
      weekday: 'short', 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const getAssessmentTypeIcon = (type: string) => {
    switch (type) {
      case "assignment": return <BookOpen className="h-4 w-4" />
      case "exam": return <AlertCircle className="h-4 w-4" />
      case "quiz": return <Clock className="h-4 w-4" />
      case "project": return <Plus className="h-4 w-4" />
      default: return <BookOpen className="h-4 w-4" />
    }
  }

  const getAssessmentTypeColor = (type: string) => {
    switch (type) {
      case "assignment": return "bg-blue-500/20 text-blue-300 border-blue-400/50"
      case "exam": return "bg-red-500/20 text-red-300 border-red-400/50"
      case "quiz": return "bg-green-500/20 text-green-300 border-green-400/50"
      case "project": return "bg-yellow-500/20 text-yellow-300 border-yellow-400/50"
      default: return "bg-gray-500/20 text-gray-300 border-gray-400/50"
    }
  }

  const exportToiCal = () => {
    let icalContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UQ Course Craft//Assessment Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
`

    assessments.forEach(assessment => {
      const dueDate = new Date(assessment.dueDate)
      if (isNaN(dueDate.getTime())) {
        return
      }
      const utcDate = dueDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'
      
      icalContent += `BEGIN:VEVENT
UID:${assessment.id}@uqcoursecraft.com
DTSTART:${utcDate}
DTEND:${utcDate}
SUMMARY:${assessment.courseCode} - ${assessment.assessmentName}
DESCRIPTION:Course: ${assessment.courseName}\nWeighting: ${assessment.weighting}%${assessment.notes ? '\nNotes: ' + assessment.notes : ''}
LOCATION:University of Queensland
END:VEVENT
`
    })

    icalContent += `END:VCALENDAR`

    const blob = new Blob([icalContent], { type: 'text/calendar' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'uq-assessments.ics'
    a.click()
    URL.revokeObjectURL(url)

    setAlertTitle("iCal File Exported!")
    setAlertDescription("Your assessment calendar has been downloaded successfully")
    setShowAlert(true)
    setTimeout(() => setShowAlert(false), 3000)
  }

  const groupAssessmentsByMonth = () => {
    const grouped = assessments.reduce((acc, assessment) => {
      const date = new Date(assessment.dueDate)
      const monthKey = !isNaN(date.getTime()) 
        ? date.toLocaleDateString('en-AU', { month: 'long', year: 'numeric' })
        : "Recurring"
      
      if (!acc[monthKey]) {
        acc[monthKey] = []
      }
      acc[monthKey].push(assessment)
      return acc
    }, {} as Record<string, Assessment[]>)

    // Sort assessments within each month by date
    Object.keys(grouped).forEach(month => {
      grouped[month].sort((a, b) => {
        const dateA = new Date(a.dueDate)
        const dateB = new Date(b.dueDate)
        
        if (isNaN(dateA.getTime())) return 1
        if (isNaN(dateB.getTime())) return -1

        return dateA.getTime() - dateB.getTime()
      })
    })

    return grouped
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900 w-screen flex items-center">
      <Alert
        className={`
          absolute top-4 right-4 w-96 transition-opacity duration-500
          text-white bg-purple-500 ${showAlert ? "opacity-100" : "opacity-0"}
        `}
        variant={"default"}
      >
        <AlertCircle />
        <AlertTitle>{alertTitle}</AlertTitle>
        <AlertDescription>{alertDescription}</AlertDescription>
      </Alert>

      {showInfoModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-purple-800 rounded-lg p-6 max-w-md w-full border border-purple-600 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Info className="h-5 w-5 text-purple-300" />
                <h2 className="text-xl font-semibold text-white">Assessment Calendar</h2>
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
                  <li>Add UQ course codes to see all assessment dates</li>
                  <li>Switch between List and Calendar views</li>
                  <li>Export to iCal for your preferred calendar app</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium text-white mb-2">Features:</h3>
                <ul className="space-y-1 list-disc list-inside">
                  <li>Automatically scrapes assessmenta dates from UQ</li>
                  <li>Includes weightings and important notes</li>
                  <li>Compatible with Google Calendar, Outlook, and more</li>
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

      {selectedAssessment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-40 p-4">
          <div className="bg-purple-800 rounded-lg p-6 max-w-lg w-full border border-purple-600 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                {getAssessmentTypeIcon(selectedAssessment.type)}
                <h2 className="text-xl font-semibold text-white">{selectedAssessment.assessmentName}</h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelectedAssessment(null)}
                className="text-purple-300 hover:bg-purple-700/50"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-4 text-purple-100">
              <div>
                <div className="text-sm opacity-80">Course</div>
                <div className="font-medium text-white">{selectedAssessment.courseCode} - {selectedAssessment.courseName}</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm opacity-80">Due Date</div>
                  <div className="font-medium text-white">{formatDate(selectedAssessment.dueDate)}</div>
                </div>
                <div>
                  <div className="text-sm opacity-80">Weighting</div>
                  <div className="font-medium text-white">{selectedAssessment.weighting}%</div>
                </div>
              </div>

              {selectedAssessment.notes && (
                <div>
                  <div className="text-sm opacity-80">Notes</div>
                  <div className="font-medium text-white">{selectedAssessment.notes}</div>
                </div>
              )}
            </div>

            <Button
              onClick={() => setSelectedAssessment(null)}
              className="w-full mt-6 bg-purple-600 hover:bg-purple-500 text-white"
            >
              Close
            </Button>
          </div>
        </div>
      )}

      <div className="px-6 flex gap-6 w-full h-screen py-4">
        {/* Left Sidebar */}
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

          {/* Search Bar */}
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

          {/* View Toggle */}
          <div className="flex items-center gap-2">
            <div className="bg-purple-700/50 rounded-lg flex">
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
                className={`rounded-r-none ${ 
                  viewMode === "list" ? "bg-purple-600 text-white" : "text-purple-200 hover:bg-purple-600/30"
                }`}
              >
                <List className="h-4 w-4 mr-2" />
                List View
              </Button>
              <Button
                variant={viewMode === "calendar" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("calendar")}
                className={`rounded-l-none ${ 
                  viewMode === "calendar" ? "bg-purple-600 text-white" : "text-purple-200 hover:bg-purple-600/30"
                }`}
              >
                <Calendar className="h-4 w-4 mr-2" />
                Calendar View
              </Button>
            </div>
          </div>

          {/* Settings */}
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

          {/* Courses List */}
          <div className="border-2 border-dashed border-purple-400/50 rounded-lg p-4 text-center min-h-[200px] flex flex-col items-center justify-center">
            {courses.length === 0 ? (
              <div className="text-purple-200 text-sm font-medium">
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-purple-400 border-t-transparent mx-auto mb-2"></div>
                    VERIFYING COURSE...
                  </>
                ) : (
                  <>
                    SEARCH TO ADD
                    <br />
                    COURSES
                  </>
                )}
              </div>
            ) : (
              <div className="w-full space-y-3">
                {courses.map((course, index) => (
                  <div
                    key={index}
                    className="w-full border-2 border-purple-400/50 border-dashed rounded-lg p-3 flex flex-col"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-sm text-white font-medium">{course.code}</span>
                        <div className="text-xs text-purple-200 opacity-80">{course.name}</div>
                      </div>
                      <Button 
                        size="sm"
                        variant="ghost"
                        className="text-red-400 hover:bg-red-500/20"
                        onClick={() => removeCourse(index)}
                      >
                        <Trash className="h-4 w-4"/>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Export Button */}
          <Button
            onClick={exportToiCal}
            disabled={assessments.length === 0}
            className="w-full bg-green-600 hover:bg-green-500 text-white disabled:bg-gray-600 disabled:opacity-50"
          >
            <Download className="h-4 w-4 mr-2" />
            Export iCal File
          </Button>
        </div>

        {/* Main Content Panel */}
        <div className="flex-1">
          <div className="bg-purple-800/30 rounded-lg overflow-hidden h-full flex flex-col">
            {assessments.length === 0 ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center text-purple-200">
                  <Calendar className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <h3 className="text-xl font-medium mb-2">No Assessments Found</h3>
                  <p className="text-sm opacity-80">Add courses to see their assessment dates</p>
                </div>
              </div>
            ) : viewMode === "list" ? (
              <div className="p-6 overflow-auto">
                <h2 className="text-2xl font-bold text-white mb-6">Assessment Overview</h2>
                
                {Object.entries(groupAssessmentsByMonth()).map(([month, monthAssessments]) => (
                  <div key={month} className="mb-8">
                    <h3 className="text-lg font-semibold text-white mb-4 border-b border-purple-600/50 pb-2">
                      {month}
                    </h3>
                    
                    <div className="space-y-3">
                      {monthAssessments.map((assessment) => (
                        <div
                          key={assessment.id}
                          onClick={() => setSelectedAssessment(assessment)}
                          className="bg-purple-700/30 rounded-lg p-4 border border-purple-600/30 hover:bg-purple-700/50 transition-colors cursor-pointer"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className={`p-2 rounded-md border ${getAssessmentTypeColor(assessment.type)}`}>
                                {getAssessmentTypeIcon(assessment.type)}
                              </div>
                              <div>
                                <div className="font-semibold text-white">{assessment.assessmentName}</div>
                                <div className="text-sm text-purple-200">{assessment.courseCode} - {assessment.courseName}</div>
                              </div>
                            </div>
                            
                            <div className="text-right">
                              <div className="text-white font-medium">{formatDate(assessment.dueDate)}</div>
                              <div className="text-sm text-purple-200">{assessment.weighting}% weighting</div>
                            </div>
                          </div>
                          
                          {assessment.notes && (
                            <div className="mt-2 pt-2 border-t border-purple-600/30">
                              <p className="text-sm text-purple-200">{assessment.notes}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 overflow-auto">
                <h2 className="text-2xl font-bold text-white mb-6">Calendar View</h2>
                
                <div className="grid grid-cols-7 gap-2 mb-4">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="text-center text-purple-200 font-medium text-sm p-2">
                      {day}
                    </div>
                  ))}
                </div>
                
                <div className="text-center text-purple-200 py-20">
                  <Calendar className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p>Calendar view coming soon!</p>
                  <p className="text-sm opacity-80 mt-2">Use List View to see all your assessments</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

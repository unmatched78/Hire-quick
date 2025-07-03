"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { User, Briefcase, MessageSquare, Calendar, MapPin, Clock, Building, Eye, Edit } from "lucide-react"

export default function CandidateDashboard() {
  const [profileCompletion] = useState(75)

  const applications = [
    {
      id: 1,
      jobTitle: "Senior Software Engineer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      appliedDate: "2024-01-15",
      status: "Interview Scheduled",
      statusColor: "bg-blue-500",
    },
    {
      id: 2,
      jobTitle: "Product Manager",
      company: "StartupXYZ",
      location: "Remote",
      appliedDate: "2024-01-12",
      status: "Under Review",
      statusColor: "bg-yellow-500",
    },
    {
      id: 3,
      jobTitle: "UX Designer",
      company: "Design Studio",
      location: "New York, NY",
      appliedDate: "2024-01-10",
      status: "Rejected",
      statusColor: "bg-red-500",
    },
  ]

  const interviews = [
    {
      id: 1,
      jobTitle: "Senior Software Engineer",
      company: "TechCorp Inc.",
      date: "2024-01-20",
      time: "2:00 PM",
      type: "Technical Interview",
      interviewer: "John Smith",
    },
    {
      id: 2,
      jobTitle: "Full Stack Developer",
      company: "WebCorp",
      date: "2024-01-22",
      time: "10:00 AM",
      type: "HR Interview",
      interviewer: "Sarah Johnson",
    },
  ]

  const recommendedJobs = [
    {
      id: 1,
      title: "Senior React Developer",
      company: "InnovaTech",
      location: "Austin, TX",
      salary: "$130k - $170k",
      match: 95,
    },
    {
      id: 2,
      title: "Frontend Engineer",
      company: "CloudSoft",
      location: "Remote",
      salary: "$110k - $150k",
      match: 88,
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Candidate Dashboard</h1>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Edit className="w-4 h-4 mr-2" />
                Edit Profile
              </Button>
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Completion */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Profile Completion
            </CardTitle>
            <CardDescription>Complete your profile to get better job recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <Progress value={profileCompletion} className="flex-1" />
              <span className="text-sm font-medium">{profileCompletion}%</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <Badge variant="outline">Add Skills</Badge>
              <Badge variant="outline">Upload Resume</Badge>
              <Badge variant="outline">Add Work Experience</Badge>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="applications" className="space-y-6">
          <TabsList>
            <TabsTrigger value="applications">My Applications</TabsTrigger>
            <TabsTrigger value="interviews">Interviews</TabsTrigger>
            <TabsTrigger value="recommended">Recommended Jobs</TabsTrigger>
            <TabsTrigger value="messages">Messages</TabsTrigger>
          </TabsList>

          <TabsContent value="applications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Briefcase className="w-5 h-5 mr-2" />
                  Job Applications
                </CardTitle>
                <CardDescription>Track the status of your job applications</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {applications.map((app) => (
                    <div key={app.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{app.jobTitle}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <span className="flex items-center">
                            <Building className="w-4 h-4 mr-1" />
                            {app.company}
                          </span>
                          <span className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            {app.location}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            Applied {app.appliedDate}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge className={`${app.statusColor} text-white`}>{app.status}</Badge>
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="interviews">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Upcoming Interviews
                </CardTitle>
                <CardDescription>Manage your scheduled interviews</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {interviews.map((interview) => (
                    <div key={interview.id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg">{interview.jobTitle}</h3>
                          <p className="text-gray-600">{interview.company}</p>
                        </div>
                        <Badge variant="outline">{interview.type}</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="font-medium">Date:</span> {interview.date}
                        </div>
                        <div>
                          <span className="font-medium">Time:</span> {interview.time}
                        </div>
                        <div>
                          <span className="font-medium">Interviewer:</span> {interview.interviewer}
                        </div>
                      </div>
                      <div className="mt-4 flex space-x-2">
                        <Button size="sm">Join Meeting</Button>
                        <Button variant="outline" size="sm">
                          Reschedule
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="recommended">
            <Card>
              <CardHeader>
                <CardTitle>Recommended Jobs</CardTitle>
                <CardDescription>Jobs matched to your profile and preferences</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recommendedJobs.map((job) => (
                    <div key={job.id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg">{job.title}</h3>
                          <p className="text-gray-600">{job.company}</p>
                          <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                            <span className="flex items-center">
                              <MapPin className="w-4 h-4 mr-1" />
                              {job.location}
                            </span>
                            <span className="text-green-600 font-medium">{job.salary}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-blue-600">{job.match}%</div>
                          <div className="text-sm text-gray-500">Match</div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm">Apply Now</Button>
                        <Button variant="outline" size="sm">
                          Save Job
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="messages">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <MessageSquare className="w-5 h-5 mr-2" />
                  Messages
                </CardTitle>
                <CardDescription>Communication with recruiters and companies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No messages yet</p>
                  <p className="text-sm text-gray-400 mt-2">Messages from recruiters will appear here</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

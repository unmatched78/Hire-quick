"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import {
  Plus,
  Users,
  Briefcase,
  BarChart3,
  Search,
  Filter,
  Eye,
  Download,
  Calendar,
  MapPin,
  Clock,
  Building,
} from "lucide-react"

export default function RecruiterDashboard() {
  const [searchTerm, setSearchTerm] = useState("")

  const jobPostings = [
    {
      id: 1,
      title: "Senior Software Engineer",
      department: "Engineering",
      location: "San Francisco, CA",
      type: "Full-time",
      posted: "2024-01-15",
      applications: 45,
      status: "Active",
    },
    {
      id: 2,
      title: "Product Manager",
      department: "Product",
      location: "Remote",
      type: "Full-time",
      posted: "2024-01-12",
      applications: 32,
      status: "Active",
    },
    {
      id: 3,
      title: "UX Designer",
      department: "Design",
      location: "New York, NY",
      type: "Contract",
      posted: "2024-01-10",
      applications: 28,
      status: "Paused",
    },
  ]

  const candidates = [
    {
      id: 1,
      name: "Alice Johnson",
      title: "Senior Software Engineer",
      location: "San Francisco, CA",
      experience: "5+ years",
      skills: ["React", "Node.js", "Python"],
      match: 95,
      status: "New",
    },
    {
      id: 2,
      name: "Bob Smith",
      title: "Product Manager",
      location: "Austin, TX",
      experience: "7+ years",
      skills: ["Product Strategy", "Analytics", "Agile"],
      match: 88,
      status: "Interviewed",
    },
    {
      id: 3,
      name: "Carol Davis",
      title: "UX Designer",
      location: "Remote",
      experience: "4+ years",
      skills: ["Figma", "User Research", "Prototyping"],
      match: 92,
      status: "Shortlisted",
    },
  ]

  const interviews = [
    {
      id: 1,
      candidate: "Alice Johnson",
      position: "Senior Software Engineer",
      date: "2024-01-20",
      time: "2:00 PM",
      type: "Technical Interview",
      interviewer: "You",
    },
    {
      id: 2,
      candidate: "Bob Smith",
      position: "Product Manager",
      date: "2024-01-22",
      time: "10:00 AM",
      type: "Final Interview",
      interviewer: "Sarah Wilson",
    },
  ]

  const stats = [
    { label: "Active Jobs", value: "12", change: "+2" },
    { label: "Total Applications", value: "234", change: "+18" },
    { label: "Interviews Scheduled", value: "8", change: "+3" },
    { label: "Hires This Month", value: "3", change: "+1" },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Recruiter Dashboard</h1>
            <div className="flex items-center space-x-4">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Post New Job
              </Button>
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                    <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className="text-sm text-green-600 font-medium">{stat.change}</div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="jobs" className="space-y-6">
          <TabsList>
            <TabsTrigger value="jobs">Job Postings</TabsTrigger>
            <TabsTrigger value="candidates">Candidates</TabsTrigger>
            <TabsTrigger value="interviews">Interviews</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="jobs">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center">
                      <Briefcase className="w-5 h-5 mr-2" />
                      Job Postings
                    </CardTitle>
                    <CardDescription>Manage your active job postings</CardDescription>
                  </div>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Post New Job
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {jobPostings.map((job) => (
                    <div key={job.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{job.title}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <span className="flex items-center">
                            <Building className="w-4 h-4 mr-1" />
                            {job.department}
                          </span>
                          <span className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            {job.location}
                          </span>
                          <span className="flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            Posted {job.posted}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{job.applications}</div>
                          <div className="text-sm text-gray-500">Applications</div>
                        </div>
                        <Badge variant={job.status === "Active" ? "default" : "secondary"}>{job.status}</Badge>
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

          <TabsContent value="candidates">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center">
                      <Users className="w-5 h-5 mr-2" />
                      Candidates
                    </CardTitle>
                    <CardDescription>Browse and manage candidate applications</CardDescription>
                  </div>
                  <div className="flex space-x-2">
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        placeholder="Search candidates..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 w-64"
                      />
                    </div>
                    <Button variant="outline">
                      <Filter className="w-4 h-4 mr-2" />
                      Filter
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {candidates.map((candidate) => (
                    <div key={candidate.id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg">{candidate.name}</h3>
                          <p className="text-gray-600">{candidate.title}</p>
                          <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                            <span className="flex items-center">
                              <MapPin className="w-4 h-4 mr-1" />
                              {candidate.location}
                            </span>
                            <span>{candidate.experience}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-3">
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600">{candidate.match}%</div>
                            <div className="text-sm text-gray-500">Match</div>
                          </div>
                          <Badge variant="outline">{candidate.status}</Badge>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-2">
                          {candidate.skills.map((skill, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm">
                            <Eye className="w-4 h-4 mr-1" />
                            View Profile
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-1" />
                            Resume
                          </Button>
                          <Button size="sm">Schedule Interview</Button>
                        </div>
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
                  Scheduled Interviews
                </CardTitle>
                <CardDescription>Manage upcoming interviews</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {interviews.map((interview) => (
                    <div key={interview.id} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="font-semibold text-lg">{interview.candidate}</h3>
                          <p className="text-gray-600">{interview.position}</p>
                        </div>
                        <Badge variant="outline">{interview.type}</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm mb-4">
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
                      <div className="flex space-x-2">
                        <Button size="sm">Join Meeting</Button>
                        <Button variant="outline" size="sm">
                          Reschedule
                        </Button>
                        <Button variant="outline" size="sm">
                          View Candidate
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="grid gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2" />
                    Recruitment Analytics
                  </CardTitle>
                  <CardDescription>Track your recruitment performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Analytics dashboard coming soon</p>
                    <p className="text-sm text-gray-400 mt-2">View detailed metrics about your recruitment process</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

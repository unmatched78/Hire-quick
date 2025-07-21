"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Search, Filter, MapPin, Clock, Building, DollarSign, Bookmark, Heart } from "lucide-react"

export default function JobsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [locationFilter, setLocationFilter] = useState("")
  const [jobTypeFilter, setJobTypeFilter] = useState("")
  const [remoteFilter, setRemoteFilter] = useState("")
  const [salaryFilter, setSalaryFilter] = useState("")

  const jobs = [
    {
      id: 1,
      title: "Senior Software Engineer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      salary: "$120k - $180k",
      type: "Full-time",
      remote: true,
      posted: "2 days ago",
      description: "We're looking for a senior software engineer to join our growing team...",
      skills: ["React", "Node.js", "TypeScript", "AWS"],
      benefits: ["Health Insurance", "401k", "Remote Work", "Flexible Hours"],
    },
    {
      id: 2,
      title: "Product Manager",
      company: "StartupXYZ",
      location: "Remote",
      salary: "$100k - $150k",
      type: "Full-time",
      remote: true,
      posted: "1 day ago",
      description: "Join our product team to drive innovation and growth...",
      skills: ["Product Strategy", "Analytics", "Agile", "User Research"],
      benefits: ["Equity", "Health Insurance", "Unlimited PTO"],
    },
    {
      id: 3,
      title: "UX Designer",
      company: "Design Studio",
      location: "New York, NY",
      salary: "$80k - $120k",
      type: "Contract",
      remote: false,
      posted: "3 days ago",
      description: "Create beautiful and intuitive user experiences...",
      skills: ["Figma", "User Research", "Prototyping", "Design Systems"],
      benefits: ["Health Insurance", "Professional Development"],
    },
    {
      id: 4,
      title: "Data Scientist",
      company: "DataCorp",
      location: "Austin, TX",
      salary: "$110k - $160k",
      type: "Full-time",
      remote: true,
      posted: "1 week ago",
      description: "Analyze complex datasets to drive business insights...",
      skills: ["Python", "Machine Learning", "SQL", "Statistics"],
      benefits: ["Health Insurance", "401k", "Stock Options", "Learning Budget"],
    },
    {
      id: 5,
      title: "DevOps Engineer",
      company: "CloudTech",
      location: "Seattle, WA",
      salary: "$130k - $170k",
      type: "Full-time",
      remote: true,
      posted: "4 days ago",
      description: "Build and maintain scalable infrastructure...",
      skills: ["AWS", "Docker", "Kubernetes", "Terraform"],
      benefits: ["Health Insurance", "401k", "Remote Work", "Conference Budget"],
    },
    {
      id: 6,
      title: "Marketing Manager",
      company: "GrowthCo",
      location: "Los Angeles, CA",
      salary: "$90k - $130k",
      type: "Full-time",
      remote: false,
      posted: "5 days ago",
      description: "Lead marketing campaigns and drive customer acquisition...",
      skills: ["Digital Marketing", "Analytics", "Content Strategy", "SEO"],
      benefits: ["Health Insurance", "401k", "Gym Membership"],
    },
  ]

  const jobTypes = ["Full-time", "Part-time", "Contract", "Internship"]
  const locations = ["Remote", "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Los Angeles, CA"]

  const filteredJobs = jobs.filter((job) => {
    const matchesSearch =
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.skills.some((skill) => skill.toLowerCase().includes(searchTerm.toLowerCase()))

    const matchesLocation = !locationFilter || job.location === locationFilter
    const matchesJobType = !jobTypeFilter || job.type === jobTypeFilter
    const matchesRemote =
      !remoteFilter ||
      (remoteFilter === "remote" && job.remote) ||
      (remoteFilter === "hybrid" && !job.remote) ||
      (remoteFilter === "onsite" && job.remote)
    const matchesSalary =
      !salaryFilter ||
      (salaryFilter === "under-50k" && Number.parseFloat(job.salary.replace(/[^0-9.]/g, "")) < 50) ||
      (salaryFilter === "50k-100k" &&
        Number.parseFloat(job.salary.replace(/[^0-9.]/g, "")) >= 50 &&
        Number.parseFloat(job.salary.replace(/[^0-9.]/g, "")) <= 100) ||
      (salaryFilter === "100k-150k" &&
        Number.parseFloat(job.salary.replace(/[^0-9.]/g, "")) > 100 &&
        Number.parseFloat(job.salary.replace(/[^0-9.]/g, "")) <= 150) ||
      (salaryFilter === "over-150k" && Number.parseFloat(job.salary.replace(/[^0-9.]/g, "")) > 150)

    return matchesSearch && matchesLocation && matchesJobType && matchesRemote && matchesSalary
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">Find Jobs</h1>
            <div className="flex items-center space-x-4">
              <Button variant="outline">
                <Bookmark className="w-4 h-4 mr-2" />
                Saved Jobs
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Filters Sidebar */}
          <div className="w-80 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Filter className="w-5 h-5 mr-2" />
                  Filters
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Search */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Search</label>
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <Input
                      placeholder="Job title, skills, company..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                {/* Location */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Location</label>
                  <Select value={locationFilter} onValueChange={setLocationFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select location" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Locations</SelectItem>
                      {locations.map((location) => (
                        <SelectItem key={location} value={location}>
                          {location}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Job Type */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Job Type</label>
                  <Select value={jobTypeFilter} onValueChange={setJobTypeFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select job type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {jobTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Remote Work */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Work Style</label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="remote"
                        checked={remoteFilter === "remote"}
                        onChange={(e) => setRemoteFilter(e.target.checked ? "remote" : "")}
                      />
                      <label htmlFor="remote" className="text-sm">
                        Remote
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="hybrid"
                        checked={remoteFilter === "hybrid"}
                        onChange={(e) => setRemoteFilter(e.target.checked ? "hybrid" : "")}
                      />
                      <label htmlFor="hybrid" className="text-sm">
                        Hybrid
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="onsite"
                        checked={remoteFilter === "onsite"}
                        onChange={(e) => setRemoteFilter(e.target.checked ? "onsite" : "")}
                      />
                      <label htmlFor="onsite" className="text-sm">
                        On-site
                      </label>
                    </div>
                  </div>
                </div>

                {/* Salary Range */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Salary Range</label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="under-50k"
                        checked={salaryFilter === "under-50k"}
                        onChange={(e) => setSalaryFilter(e.target.checked ? "under-50k" : "")}
                      />
                      <label htmlFor="under-50k" className="text-sm">
                        Under $50k
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="50k-100k"
                        checked={salaryFilter === "50k-100k"}
                        onChange={(e) => setSalaryFilter(e.target.checked ? "50k-100k" : "")}
                      />
                      <label htmlFor="50k-100k" className="text-sm">
                        $50k - $100k
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="100k-150k"
                        checked={salaryFilter === "100k-150k"}
                        onChange={(e) => setSalaryFilter(e.target.checked ? "100k-150k" : "")}
                      />
                      <label htmlFor="100k-150k" className="text-sm">
                        $100k - $150k
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="over-150k"
                        checked={salaryFilter === "over-150k"}
                        onChange={(e) => setSalaryFilter(e.target.checked ? "over-150k" : "")}
                      />
                      <label htmlFor="over-150k" className="text-sm">
                        Over $150k
                      </label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Job Listings */}
          <div className="flex-1">
            <div className="mb-6 flex justify-between items-center">
              <p className="text-gray-600">
                Showing {filteredJobs.length} of {jobs.length} jobs
              </p>
              <Select defaultValue="newest">
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="newest">Newest First</SelectItem>
                  <SelectItem value="oldest">Oldest First</SelectItem>
                  <SelectItem value="salary-high">Salary: High to Low</SelectItem>
                  <SelectItem value="salary-low">Salary: Low to High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-6">
              {filteredJobs.map((job) => (
                <Card key={job.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="secondary">{job.type}</Badge>
                          {job.remote && <Badge variant="outline">Remote</Badge>}
                          <div className="flex items-center text-sm text-gray-500">
                            <Clock className="w-4 h-4 mr-1" />
                            {job.posted}
                          </div>
                        </div>
                        <CardTitle className="text-xl mb-2">{job.title}</CardTitle>
                        <CardDescription className="flex items-center space-x-4 text-base">
                          <span className="flex items-center">
                            <Building className="w-4 h-4 mr-1" />
                            {job.company}
                          </span>
                          <span className="flex items-center">
                            <MapPin className="w-4 h-4 mr-1" />
                            {job.location}
                          </span>
                          <span className="flex items-center text-green-600 font-semibold">
                            <DollarSign className="w-4 h-4 mr-1" />
                            {job.salary}
                          </span>
                        </CardDescription>
                      </div>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm">
                          <Heart className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Bookmark className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4 line-clamp-2">{job.description}</p>

                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">Required Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {job.skills.map((skill, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium mb-2">Benefits</h4>
                        <div className="flex flex-wrap gap-2">
                          {job.benefits.map((benefit, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {benefit}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="flex space-x-3 mt-6">
                      <Button className="flex-1">Apply Now</Button>
                      <Button variant="outline">View Details</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredJobs.length === 0 && (
              <Card>
                <CardContent className="text-center py-12">
                  <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No jobs found</h3>
                  <p className="text-gray-600">
                    Try adjusting your search criteria or filters to find more opportunities.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

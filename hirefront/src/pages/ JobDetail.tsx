import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BriefcaseIcon } from '@heroicons/react/24/solid';
import axios from 'axios';

const MotionDiv = motion.div;

interface Job {
  id: number;
  title: string;
  description: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  job_type: string;
  posted_by: { name: string };
  date_posted: string;
}

const JobDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/jobs/${id}/`);
        setJob(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load job details');
        setLoading(false);
      }
    };
    fetchJob();
  }, [id]);

  const handleApply = () => {
    navigate('/apply');
  };

  if (loading) return <div className="text-center text-brand-500">Loading...</div>;
  if (error) return <div className="text-center text-red-500">{error}</div>;

  return (
    <MotionDiv
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mx-auto mt-10 max-w-3xl rounded-lg bg-gray-800 p-8 shadow-lg glow"
    >
      <div className="space-y-6">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-brand-500 to-brand-600 bg-clip-text text-transparent">
          {job?.title}
        </h2>
        <div className="flex items-center">
          <BriefcaseIcon className="w-6 h-6 text-brand-500 mr-2" />
          <span className="text-lg font-bold text-white">{job?.posted_by.name}</span>
        </div>
        <p className="text-white"><strong>Location:</strong> {job?.location}</p>
        <p className="text-white"><strong>Job Type:</strong> {job?.job_type}</p>
        {(job?.salary_min || job?.salary_max) && (
          <p className="text-white">
            <strong>Salary:</strong> ${job?.salary_min?.toLocaleString()} - ${job?.salary_max?.toLocaleString()}
          </p>
        )}
        <p className="text-white"><strong>Posted:</strong> {new Date(job?.date_posted || '').toLocaleDateString()}</p>
        <p className="text-white"><strong>Description:</strong> {job?.description}</p>
        <button
          onClick={handleApply}
          className="rounded-md bg-brand-500 px-6 py-3 text-white hover:bg-brand-600"
        >
          Apply Now
        </button>
      </div>
    </MotionDiv>
  );
};

export default JobDetail;
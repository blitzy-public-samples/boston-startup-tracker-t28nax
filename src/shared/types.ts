// Shared type definitions for the Boston Startup Tracker

// Interface representing a startup company
export interface Startup {
  id: number;
  name: string;
  website: string;
  industry: string;
  subSector: string;
  employeeCount: number;
  localEmployeeCount: number;
  headcountGrowthRate: number;
  totalFunding: number;
  lastFundingDate: Date;
  fundingStage: string;
  isHiring: boolean;
  lastUpdated: Date;
}

// Interface representing an investor
export interface Investor {
  id: number;
  name: string;
  type: string;
  website: string;
}

// Interface representing a funding round
export interface FundingRound {
  id: number;
  startupId: number;
  amount: number;
  date: Date;
  roundType: string;
  investors: Investor[];
}

// Interface representing a job posting
export interface JobPosting {
  id: number;
  startupId: number;
  title: string;
  department: string;
  description: string;
  postedDate: Date;
  isActive: boolean;
}

// Interface representing a news article
export interface NewsArticle {
  id: number;
  startupId: number;
  title: string;
  url: string;
  publishedDate: Date;
  source: string;
  summary: string;
}

// Interface representing a user
export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  createdAt: Date;
  lastLogin: Date;
}

// Enum representing user roles
export enum UserRole {
  ADMIN = 'ADMIN',
  USER = 'USER',
  PREMIUM_USER = 'PREMIUM_USER'
}
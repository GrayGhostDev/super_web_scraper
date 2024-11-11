from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Basic Information
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    location = Column(String)
    
    # Professional Information
    title = Column(String)
    company = Column(String)
    industry = Column(String)
    
    # Social Profiles
    linkedin_url = Column(String)
    twitter_url = Column(String)
    
    # Verification Status
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    
    # Additional Data
    raw_data = Column(JSON)
    confidence_score = Column(Float)
    
    # Relationships
    company_id = Column(Integer, ForeignKey('companies.id'))
    company_info = relationship("Company", back_populates="profiles")
    experiences = relationship("Experience", back_populates="profile")
    educations = relationship("Education", back_populates="profile")

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    name = Column(String)
    domain = Column(String)
    industry = Column(String)
    size = Column(String)
    location = Column(String)
    linkedin_url = Column(String)
    website = Column(String)
    
    # Additional Data
    raw_data = Column(JSON)
    
    # Relationships
    profiles = relationship("Profile", back_populates="company_info")

class Experience(Base):
    __tablename__ = 'experiences'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    
    title = Column(String)
    company = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String)
    description = Column(String)
    
    profile = relationship("Profile", back_populates="experiences")

class Education(Base):
    __tablename__ = 'educations'
    
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profiles.id'))
    
    school = Column(String)
    degree = Column(String)
    field = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    profile = relationship("Profile", back_populates="educations")
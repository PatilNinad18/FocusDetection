import React from 'react'
import CalendarDisplay from './CalenderDisplay'
import { Clock } from 'react-feather'

function Navbar() {
  return (
    <div className="fixed top-0 left-0 w-full h-16 flex items-center justify-between px-8 bg-transparent backdrop-blur-sm">
  {/* Left Section */}
  <h3 className="text-white drop-shadow-md text-4xl font-bold flex">
    <Clock size={36} className='gap-5'/>

    FocusTracker
  </h3>

  {/* Right Section */}
  <div className="flex items-center gap-6">
    
    <CalendarDisplay/>
    <p className="text-white-400 text-sm">Focused: 42m</p>
  </div>
</div>

  )
}

export default Navbar

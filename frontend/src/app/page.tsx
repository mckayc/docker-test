import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-medieval text-medieval-wood mb-8">
          Welcome to Task Donegeon
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* Daily Quests */}
          <div className="card">
            <h2 className="text-2xl font-medieval text-medieval-wood mb-4">
              Daily Quests
            </h2>
            <p className="text-medieval-leather mb-4">
              Complete your daily tasks to earn experience and gold!
            </p>
            <Link href="/tasks/daily" className="btn btn-primary">
              View Daily Quests
            </Link>
          </div>

          {/* Weekly Missions */}
          <div className="card">
            <h2 className="text-2xl font-medieval text-medieval-wood mb-4">
              Weekly Missions
            </h2>
            <p className="text-medieval-leather mb-4">
              Take on bigger challenges for greater rewards!
            </p>
            <Link href="/tasks/weekly" className="btn btn-primary">
              View Weekly Missions
            </Link>
          </div>

          {/* Epic Quests */}
          <div className="card">
            <h2 className="text-2xl font-medieval text-medieval-wood mb-4">
              Epic Quests
            </h2>
            <p className="text-medieval-leather mb-4">
              Long-term goals with legendary rewards!
            </p>
            <Link href="/tasks/epic" className="btn btn-primary">
              View Epic Quests
            </Link>
          </div>

          {/* Character Stats */}
          <div className="card">
            <h2 className="text-2xl font-medieval text-medieval-wood mb-4">
              Character Stats
            </h2>
            <p className="text-medieval-leather mb-4">
              Check your level, experience, and achievements!
            </p>
            <Link href="/profile" className="btn btn-primary">
              View Character
            </Link>
          </div>

          {/* Inventory */}
          <div className="card">
            <h2 className="text-2xl font-medieval text-medieval-wood mb-4">
              Inventory
            </h2>
            <p className="text-medieval-leather mb-4">
              Manage your items and equipment!
            </p>
            <Link href="/inventory" className="btn btn-primary">
              Open Inventory
            </Link>
          </div>

          {/* Achievements */}
          <div className="card">
            <h2 className="text-2xl font-medieval text-medieval-wood mb-4">
              Achievements
            </h2>
            <p className="text-medieval-leather mb-4">
              View your completed achievements and unlock new ones!
            </p>
            <Link href="/achievements" className="btn btn-primary">
              View Achievements
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
} 
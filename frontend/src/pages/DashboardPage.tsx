import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DollarSign, CreditCard, PiggyBank, TrendingUp } from 'lucide-react'

const stats = [
  {
    title: 'Total Balance',
    value: '$12,234.56',
    change: '+2.5%',
    changeType: 'positive' as const,
    icon: DollarSign,
  },
  {
    title: 'Total Accounts',
    value: '4',
    change: '0',
    changeType: 'neutral' as const,
    icon: CreditCard,
  },
  {
    title: 'Monthly Budget',
    value: '$3,500',
    change: '75% used',
    changeType: 'warning' as const,
    icon: PiggyBank,
  },
  {
    title: 'Goals Progress',
    value: '3 of 5',
    change: '60% complete',
    changeType: 'positive' as const,
    icon: TrendingUp,
  },
]

export const DashboardPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's an overview of your financial situation.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className={`text-xs ${
                  stat.changeType === 'positive'
                    ? 'text-green-600'
                    : stat.changeType === 'warning'
                    ? 'text-yellow-600'
                    : 'text-muted-foreground'
                }`}>
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
            <CardDescription>
              Your latest financial activity
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Transaction {i}</p>
                    <p className="text-sm text-muted-foreground">
                      Account {i}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">-$45.67</p>
                    <p className="text-sm text-muted-foreground">
                      2 days ago
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Budget Overview</CardTitle>
            <CardDescription>
              This month's spending by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {['Food', 'Transport', 'Entertainment'].map((category, i) => (
                <div key={category} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{category}</span>
                    <span>${(300 - i * 50).toFixed(2)} / $400.00</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${(300 - i * 50) / 4}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
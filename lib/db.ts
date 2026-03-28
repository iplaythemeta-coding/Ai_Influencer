// Stubbed DB Models for Prototype

export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

export interface FunnelState {
  userId: string;
  optInCompleted: boolean;
  tripwirePurchased: boolean;
  coreProductTier: 'none' | 'starter' | 'pro' | 'ultimate';
}

export const mockDb = {
  users: [] as User[],
  funnelStates: [] as FunnelState[],
  
  async saveUser(name: string, email: string): Promise<User> {
    const user: User = {
      id: `usr_${Math.random().toString(36).substring(2, 9)}`,
      name,
      email,
      createdAt: new Date()
    };
    this.users.push(user);
    
    this.funnelStates.push({
      userId: user.id,
      optInCompleted: true,
      tripwirePurchased: false,
      coreProductTier: 'none'
    });
    
    return user;
  }
};

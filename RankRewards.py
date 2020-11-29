import discord
import asyncio
import logging
from peewee import *
from datetime import date, timedelta

import query
import constants
from models import RankRewardModel, UserStatModel, RankModel

class RankRewards():
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings

    async def distribute_rewards(self):
        today = date.today()
        give_weekly_date = self.give_weekly_rewards(today)
        if give_weekly_date is not None:
            await self.give_weekly(give_weekly_date)
        
        give_monthly_date = self.give_monthly_rewards(today)
        if give_monthly_date is not None:
            await self.give_monthly(give_monthly_date)
    
    async def give_weekly(self, start_date):
        rewards = []
        try:
            rank_reward = (RankRewardModel  
                            .get(
                                (RankRewardModel.start_date == start_date) &
                                (RankRewardModel.reward_type == 'week')
                                )
                            )
            rewards.append(rank_reward.place_1)
            rewards.append(rank_reward.place_2)
            rewards.append(rank_reward.place_3)
        except DoesNotExist:
            logging.critical(f'RankRewards.give_weekly: RankRewards are missing. start_date: {start_date}')
            rewards.append('missing_emote')
            rewards.append('missing_emote')
            rewards.append('missing_emote')
        except Exception as e:
            logging.critical(f'RankRewards.give_weekly: {e}')
            return
        
        end_date = start_date + timedelta(days=6)
        days = 6
        
        await self.give_rewards(start_date, end_date, rewards, days, "Weekly winners")

    async def give_monthly(self, start_date):
        rewards = []
        try:
            rank_reward = (RankRewardModel  
                            .get(
                                (RankRewardModel.start_date == start_date) &
                                (RankRewardModel.reward_type == 'month')
                                )
                            )
            rewards.append(rank_reward.place_1)
            rewards.append(rank_reward.place_2)
            rewards.append(rank_reward.place_3)
        except DoesNotExist:
            logging.critical(f'RankRewards.give_monthly: RankRewards are missing. start_date: {start_date}')
            rewards.append('missing_emote')
            rewards.append('missing_emote')
            rewards.append('missing_emote')
        except Exception as e:
            logging.critical(f'RankRewards.give_monthly: {e}')
            return
        
        end_date = None
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        days = (end_date - start_date).days
        
        await self.give_rewards(start_date, end_date, rewards, days, "Monthly winners")
    
    async def give_rewards(self, start_date, end_date, rewards, days, title):
        top3 = (UserStatModel
                .select(fn.SUM(UserStatModel.catches).alias('sum_catches'), UserStatModel.user_id)
                .where(
                    (UserStatModel.date >= start_date) &
                    (UserStatModel.date <= end_date)
                    )
                .group_by(UserStatModel.user_id)
                .order_by(fn.SUM(UserStatModel.catches).desc())
                .limit(3)
                )

        winners = []
        rank = 1
        for user in top3:
            RankModel.create(start_date=start_date, duration=days, reward=rewards[rank - 1], placement=rank, user_id=user.user_id.user_id)
            winners.append((query.get_user_by_userid(user.user_id.user_id).discord_id, user.sum_catches))
            rank += 1
        announcement_embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{title}')
        
        output = ''
        rank = 1
        for winner in winners:
            output += f'**{rank}. <@{winner[0]}>**: {rewards[rank - 1]}\nTotal catches: {winner[1]:,}\n\n'
            rank += 1
        announcement_embed.add_field(name=f'{start_date} - {end_date}', value=output, inline=False)
        
        channel = self.bot.get_channel(self.settings.announcement_channel)
        # channel = self.bot.get_channel(777055535228911666) # Test channel
        await channel.send(embed=announcement_embed)
    
    # Returns true if should give out weekly rewards
    def give_weekly_rewards(self, now):
        if now.weekday() == 0:
            return now - timedelta(days=7)
        return None

    # Returns true if should give out monthly rewards
    def give_monthly_rewards(self, now):
        if now.day == 1:
            end_last_month = now - timedelta(days=1)
            return date(end_last_month.year, end_last_month.month, 1)
        return None
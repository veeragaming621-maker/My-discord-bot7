import discord
from discord.ext import commands
import google.generativeai as genai
import os

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    @commands.command()
    async def ask(self, ctx, *, question):
        """Ask the AI a question"""
        if not self.model:
            await ctx.send("❌ AI not configured! Set GEMINI_API_KEY in .env")
            return
        
        async with ctx.typing():
            try:
                response = self.model.generate_content(question)
                
                if len(response.text) > 2000:
                    chunks = [response.text[i:i+2000] for i in range(0, len(response.text), 2000)]
                    for chunk in chunks:
                        embed = discord.Embed(title="🤖 AI Response", description=chunk, color=0x00ff00)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="🤖 AI Response", description=response.text, color=0x00ff00)
                    await ctx.send(embed=embed)
            
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)[:100]}")

    @commands.command()
    async def summarize(self, ctx, *, text):
        """Summarize text"""
        if not self.model:
            await ctx.send("❌ AI not configured!")
            return
        
        async with ctx.typing():
            try:
                prompt = f"Summarize this in 1-2 sentences:\n\n{text}"
                response = self.model.generate_content(prompt)
                
                embed = discord.Embed(title="📝 Summary", description=response.text, color=0x0099ff)
                await ctx.send(embed=embed)
            
            except Exception as e:
                await ctx.send(f"❌ Error: {str(e)[:100]}")

async def setup(bot):
    await bot.add_cog(AI(bot))
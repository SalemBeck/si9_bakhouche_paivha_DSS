<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8"/>
  
  <xsl:key name="station-by-id" match="station" use="@id"/>
  
  <xsl:template match="/">
    <html>
      <body>
        <xsl:apply-templates select="transport/lines/line"/>
      </body>
    </html>
  </xsl:template>
  
  <xsl:template match="line">
    <xsl:variable name="dep" select="key('station-by-id', @departure)/@name"/>
    <xsl:variable name="arr" select="key('station-by-id', @arrival)/@name"/>
    <h2>Line: <xsl:value-of select="@code"/> (<xsl:value-of select="$dep"/> -&gt; <xsl:value-of select="$arr"/>)</h2>
    <xsl:apply-templates select="trips/trip">
      <xsl:with-param name="dep" select="$dep"/>
      <xsl:with-param name="arr" select="$arr"/>
    </xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="trip">
    <xsl:param name="dep"/>
    <xsl:param name="arr"/>
    <h3>Trip <xsl:value-of select="@code"/>: <xsl:value-of select="$dep"/> → <xsl:value-of select="$arr"/></h3>
    <p>Days: <xsl:value-of select="days"/></p>
    <table border="1">
      <thead>
        <tr><th>Schedule</th><th>Type</th><th>Class</th><th>Price</th></tr>
      </thead>
      <tbody>
        <xsl:apply-templates select="class">
          <xsl:with-param name="dep_time" select="schedule/@departure"/>
          <xsl:with-param name="arr_time" select="schedule/@arrival"/>
          <xsl:with-param name="train_type" select="@type"/>
        </xsl:apply-templates>
      </tbody>
    </table>
  </xsl:template>
  
  <xsl:template match="class">
    <xsl:param name="dep_time"/>
    <xsl:param name="arr_time"/>
    <xsl:param name="train_type"/>
    <tr>
      <td><xsl:value-of select="$dep_time"/> - <xsl:value-of select="$arr_time"/></td>
      <td><xsl:value-of select="$train_type"/></td>
      <td><xsl:value-of select="@type"/></td>
      <td><xsl:value-of select="@price"/> DA</td>
    </tr>
  </xsl:template>
  
</xsl:stylesheet>
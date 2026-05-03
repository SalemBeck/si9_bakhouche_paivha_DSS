<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="UTF-8"/>

<xsl:key name="station-by-id" match="station" use="@id"/>

<xsl:template match="/">


  <xsl:template match="line">
    <xsl:variable name="dep" select="key('station-by-id', @departure)/@name"/>
    <xsl:variable name="arr" select="key('station-by-id', @arrival)/@name"/>
    <div class="line-section">
      <div class="line-title">
        Line: <xsl:value-of select="@code"/> (
        <span><xsl:value-of select="$dep"/></span>
        -&gt;
        <span><xsl:value-of select="$arr"/></span>
        )
      </div>
      <b>Detailed List of Trips:</b>
      <xsl:apply-templates select="trips/trip">
        <xsl:with-param name="dep" select="$dep"/>
        <xsl:with-param name="arr" select="$arr"/>
      </xsl:apply-templates>
    </div>
  </xsl:template>

  <xsl:template match="trip">
    <xsl:param name="dep"/>
    <xsl:param name="arr"/>
    <div class="trip-label">
      Trip No. <xsl:value-of select="@code"/>:
      Departure: <span><xsl:value-of select="$dep"/></span>
      | Arrival: <span><xsl:value-of select="$arr"/></span>
    </div>
    <div class="days">Days: <xsl:value-of select="days"/></div>
    <table>
      <thead>
        <tr>
          <th>Schedule</th>
          <th>Train Type</th>
          <th>Class</th>
          <th>Price (DA)</th>
        </tr>
      </thead>
      <tbody>
        <xsl:apply-templates select="class">
          <xsl:with-param name="train_type" select="@type"/>
          <xsl:with-param name="dep_time" select="schedule/@departure"/>
          <xsl:with-param name="arr_time" select="schedule/@arrival"/>
        </xsl:apply-templates>
      </tbody>
    </table>
  </xsl:template>

  <xsl:template match="class">
    <xsl:param name="train_type"/>
    <xsl:param name="dep_time"/>
    <xsl:param name="arr_time"/>
    <tr>
      <td><xsl:value-of select="$dep_time"/> - <xsl:value-of select="$arr_time"/></td>
      <td><xsl:value-of select="$train_type"/></td>
      <td>
        <xsl:choose>
          <xsl:when test="@type='VIP'">
            <span class="vip">VIP</span>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@type"/>
          </xsl:otherwise>
        </xsl:choose>
      </td>
      <td>
        <xsl:choose>
          <xsl:when test="@type='VIP'">
            <span class="vip"><xsl:value-of select="@price"/></span>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@price"/>
          </xsl:otherwise>
        </xsl:choose>
      </td>
    </tr>
  </xsl:template>
</xsl:template>

</xsl:stylesheet>
